# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from collections import namedtuple
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.apps.registry import registry
from yepes.cache import LookupTable
from yepes.loading import get_model
from yepes.model_mixins import (
    Displayable,
    Illustrated,
    Logged,
    MetaData,
    Nestable,
    Orderable,
    ParentForeignKey,
    Slugged,
)
from yepes.types import Undefined
from yepes.urlresolvers import build_full_url, full_reverse
from yepes.utils import slugify

from marchena.managers import CommentManager

FakeDate = namedtuple('FakeDate', 'year, month, day')


@python_2_unicode_compatible
class AbstractBlog(Illustrated, Slugged, MetaData, Logged):

    title = models.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Title'))
    subtitle = models.CharField(
            blank=True,
            max_length=255,
            verbose_name=_('Subtitle'),
            help_text=_('In a few words, explain what this site is about.'))
    description = fields.RichTextField(
            blank=True,
            verbose_name=_('Description'),
            help_text=_('Or, maybe, you want to write a more detailed explanation.'))

    authors = models.ManyToManyField(
            'Author',
            related_name='blogs',
            verbose_name=_('Authors'))

    cache = LookupTable(['slug'], ['authors', 'categories'])

    class Meta:
        abstract = True
        folder_name = 'blog_images'
        ordering = ['title']
        verbose_name = _('Blog')
        verbose_name_plural = _('Blogs')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        kwargs = {
            #'blog_pk': self.pk,
            'blog_slug': self.slug,
        }
        return reverse('post_list', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {
            #'blog_pk': self.pk,
            'blog_slug': self.slug,
        }
        return full_reverse('post_feed', kwargs=kwargs)

    def get_upload_path(self, filename):
        filename = self.slug.replace('-', '_')
        return super(AbstractBlog, self).get_upload_path(filename)

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('title__icontains', )


@python_2_unicode_compatible
class AbstractCategory(Illustrated, Slugged, MetaData):

    blog = models.ForeignKey(
            'Blog',
            related_name='categories',
            verbose_name=_('Blog'))
    name = models.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Name'))
    description = models.TextField(
            blank=True,
            verbose_name=_('Description'),
            help_text=_('The description is usually not prominent.'))

    class Meta:
        abstract = True
        folder_name = 'blog_categories'
        ordering = ['name']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {
            #'blog_pk': self.get_blog().pk,
            'blog_slug': self.get_blog().slug,
            #'category_pk': self.pk,
            'category_slug': self.slug,
        }
        return reverse('post_list', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {
            #'blog_pk': self.get_blog().pk,
            'blog_slug': self.get_blog().slug,
            #'category_pk': self.pk,
            'category_slug': self.slug,
        }
        return full_reverse('post_feed', kwargs=kwargs)

    def get_upload_path(self, filename):
        filename = self.slug.replace('-', '_')
        return super(AbstractCategory, self).get_upload_path(filename)

    # CUSTOM METHODS

    def get_blog(self):
        Blog = get_model('marchena', 'Blog')
        return Blog.cache.get(self.blog_id)
    get_blog.short_description = _('Blog')

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )


@python_2_unicode_compatible
class AbstractComment(Nestable, Logged):

    post = models.ForeignKey(
            'Post',
            related_name='comments',
            verbose_name=_('Post'))
    parent = ParentForeignKey(
            'self',
            null=True,
            related_name='children',
            verbose_name=_('Parent comment'))

    user = models.ForeignKey(
            get_user_model(),
            null=True,
            related_name='comments',
            verbose_name=_('User'))
    author_name = models.CharField(
            blank=True,
            max_length=63,
            verbose_name=_("Author's name"))
    author_email = models.EmailField(
            blank=True,
            max_length=63,
            verbose_name=_("Author's email address"))
    author_url = models.URLField(
            blank=True,
            max_length=127,
            verbose_name=_("Author's URL"))
    ip_address = models.IPAddressField(
            blank=True,
            null=True,
            verbose_name=_('IP address'))

    karma = models.IntegerField(
            default=0,
            blank=True,
            verbose_name=_('Karma'))
    status = models.ForeignKey(
            'CommentStatus',
            default=lambda: registry['marchena:COMMENTS_INITIAL_STATUS'],
            on_delete=models.PROTECT,
            related_name='comments',
            verbose_name=_('Status'))
    is_published = models.BooleanField(
            editable=False,
            default=True,
            verbose_name=_('Is published?'))

    content = fields.RichTextField(
            blank=True,
            verbose_name=_('Content'))

    objects = CommentManager()
    search_fields = {'content': 1}

    class Meta:
        abstract = True
        ordering = ['-creation_date']
        permissions = [("can_moderate", "Can moderate comments")]
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    _author_email = Undefined
    _author_name = Undefined

    def __init__(self, *args, **kwargs):
        super(AbstractComment, self).__init__(*args, **kwargs)
        self.old_status_id = self.status_id

    def __str__(self):
        return self.get_content()

    def save(self, **kwargs):
        updated_fields = kwargs.get('update_fields', ())
        new_record = (kwargs.get('force_insert', False)
                      or not (self.pk or updated_fields))

        if self.user_id:
            self.author_name = ''
            self.author_email = ''

        if (not updated_fields
                and (new_record or self.status_id != self.old_status_id)):
            status = self.get_status()
            self.is_published = status.publish_comment
            self.old_status_id = status.id

        self._author_email = Undefined
        self._author_name = Undefined
        super(AbstractComment, self).save(**kwargs)

    def get_absolute_url(self, anchor_pattern=None):
        return '{0}{1}'.format(self.post.get_absolute_url(),
                               self.get_anchor(anchor_pattern))

    def get_anchor(self, anchor_pattern=None):
        kwargs = {
            'id': self.id,
            'post_id': self.post_id,
            'parent_id': self.parent_id,
        }
        if anchor_pattern is None:
            anchor_pattern = registry['marchena:COMMENTS_ANCHOR_PATTERN']
        return anchor_pattern.format(**kwargs)

    def get_full_url(self, anchor_pattern=None):
        return build_full_url(self.get_absolute_url(anchor_pattern))

    # CUSTOM METHODS

    def get_author_email(self):
        if self._author_email is Undefined:
            if self.user_id is None:
                self._author_email = self.author_email
            else:
                self._author_email = self.user.email

        return self._author_email
    get_author_email.short_description = _("Author's email address")

    def get_author_name(self):
        if self._author_name is Undefined:
            if self.user_id is None:
                self._author_name = self.author_name
            else:
                self._author_name = (self.user.get_full_name()
                                     or self.user.get_username())

        return self._author_name
    get_author_name.short_description = _("Author's name")

    def get_author_url(self):
        return self.author_url
    get_author_url.short_description = _("Author's URL")

    def get_content(self):
        return self.get_status().comment_replacement or self.content
    get_content.short_description = _('Content')

    def get_excerpt(self, max_words=100, end_text='...'):
        return Truncator(self.content_html).words(max_words, end_text, True)
    get_excerpt.short_description = _('Excerpt')

    def get_status(self):
        return CommentStatus.cache.get(self.status_id)
    get_excerpt.short_description = _('Status')

    # PROPERTIES

    @property
    def author_info(self):
        """
        A dictionary that pulls together information about the author
        safely for both authenticated and non-authenticated comments.

        This dict will have ``name``, ``email``, and ``url`` fields.

        """
        return {
            'name': self.get_author_name(),
            'email': self.get_author_email(),
            'url': self.get_author_url(),
        }


@python_2_unicode_compatible
class AbstractCommentStatus(Orderable):

    label = models.CharField(
            max_length=63,
            verbose_name=_('Label'))
    api_id = fields.KeyField(
            unique=True,
            verbose_name=_('API id'),
            help_text=_('This field is for internally identify the comment status. '
                        'Can only contain lowercase letters, numbers and underscores.'))
    publish_comment = models.BooleanField(
            default=True,
            verbose_name=_('Are comments published?'),
            help_text=_('Uncheck this box to make the comments effectively '
                        'disappear from the blog.'))
    comment_replacement = models.TextField(
            blank=True,
            verbose_name=_('Comment replacement'),
            help_text=_('The content of this field will replace the text of'
                        ' the user comments. E.g.: "Inappropriate comment."'))

    cache = LookupTable(['api_id'])

    class Meta:
        abstract = True
        ordering = ['label']
        verbose_name = _('Comment Status')
        verbose_name_plural = _('Comment Statuses')

    def __str__(self):
        return self.label

    def save(self, **kwargs):
        super(AbstractCommentStatus, self).save(**kwargs)
        self.comments.update(is_published=self.publish_comment)

    def natural_key(self):
        return (self.api_id, )

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('label__icontains', 'api_id__icontains')


@python_2_unicode_compatible
class AbstractLink(Illustrated, Logged):

    blog = models.ForeignKey(
            'Blog',
            related_name='links',
            verbose_name=_('Blog'))
    name = models.CharField(
            max_length=63,
            verbose_name=_('Name'),
            help_text=_('Example: A framework for perfectionists'))
    url = models.URLField(
            max_length=127,
            verbose_name=_('URL'),
            help_text=_("Example: <code>http://www.djangoproject.com/</code> &mdash; don't forget the <code>http://</code>"))
    description = models.CharField(
            max_length=255,
            blank=True,
            verbose_name=_('Description'),
            help_text=_('This will be shown when someone hovers the link in the blogroll, or optionally below the link.'))

    category = models.ForeignKey(
            'LinkCategory',
            null=True,
            related_name='links',
            verbose_name=_('Category'))

    class Meta:
        abstract = True
        folder_name = 'blog_links'
        ordering = ['name']
        verbose_name = _('Link')
        verbose_name_plural = _('Links')

    def __str__(self):
        return self.name

    def get_upload_path(self, filename):
        filename = slugify(self.name, ascii=True).replace('-', '_')
        return super(AbstractLink, self).get_upload_path(filename)

    # CUSTOM METHODS

    def get_blog(self):
        Blog = get_model('marchena', 'Blog')
        return Blog.cache.get(self.blog_id)
    get_blog.short_description = _('Blog')


@python_2_unicode_compatible
class AbstractLinkCategory(Slugged):

    blog = models.ForeignKey(
            'Blog',
            related_name='link_categories',
            verbose_name=_('Blog'))
    name = models.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Name'))
    description = models.TextField(
            blank=True,
            verbose_name=_('Description'),
            help_text=_('The description is usually not prominent.'))

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Link Category')
        verbose_name_plural = _('Link Categories')

    def __str__(self):
        return self.name

    # CUSTOM METHODS

    def get_blog(self):
        Blog = get_model('marchena', 'Blog')
        return Blog.cache.get(self.blog_id)
    get_blog.short_description = _('Blog')

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )


@python_2_unicode_compatible
class AbstractPost(Displayable, Logged):

    blog = models.ForeignKey(
            'Blog',
            related_name='posts',
            verbose_name=_('Blog'))
    guid = fields.GuidField(
            editable=False,
            verbose_name=_('Global Unique Identifier'))
    title = models.CharField(
            max_length=255,
            verbose_name=_('Title'))
    subtitle = models.CharField(
            blank=True,
            max_length=255,
            verbose_name=_('Subtitle'),
            help_text=_('Subtitles are optional complements of your title.'))
    excerpt = fields.RichTextField(
            blank=True,
            verbose_name=_('Excerpt'),
            help_text=_('Excerpts are optional hand-crafted summaries of your content.'))
    content = fields.RichTextField(
            blank=True,
            verbose_name=_('Content'))

    authors = models.ManyToManyField(
            'Author',
            limit_choices_to={'is_staff': True},
            related_name='posts',
            verbose_name=_('Authors'))
    categories = models.ManyToManyField(
            'Category',
            blank=True,
            related_name='posts',
            verbose_name=_('Categories'))
    tags = models.ManyToManyField(
            'Tag',
            blank=True,
            related_name='posts',
            verbose_name=_('Tags'))

    comment_status = models.BooleanField(
            default=True,
            verbose_name=_('Allow comments on this post'))
    comment_count = models.PositiveIntegerField(
            default=0,
            blank=True,
            verbose_name=_('Comments'))
    ping_status = models.BooleanField(
            default=True,
            verbose_name=_('Allow trackbacks and pingbacks to this post'))
    ping_count = models.PositiveIntegerField(
            default=0,
            blank=True,
            verbose_name=_('Ping count'))

    search_fields = {'title': 5, 'content': 1}

    class Meta:
        abstract = True
        ordering = ['-publish_from']
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    _images = Undefined

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        self._images = Undefined
        super(AbstractPost, self).save(**kwargs)

    def get_absolute_url(self):
        #post_date = self.get_publish_date()
        kwargs = {
            #'blog_pk': self.get_blog().pk,
            'blog_slug': self.get_blog().slug,
            #'post_pk': self.pk,
            'post_guid': self.guid,
            #'post_slug': self.slug,
            #'post_year': '{0:0>4}'.format(post_date.year),
            #'post_month': '{0:0>2}'.format(post_date.month),
            #'post_day': '{0:0>2}'.format(post_date.day),
        }
        return reverse('post_detail', kwargs=kwargs)

    def get_feed_url(self):
        #post_date = self.get_publish_date()
        kwargs = {
            #'blog_pk': self.get_blog().pk,
            'blog_slug': self.get_blog().slug,
            #'post_pk': self.pk,
            'post_guid': self.guid,
            #'post_slug': self.slug,
            #'post_year': '{0:0>4}'.format(post_date.year),
            #'post_month': '{0:0>2}'.format(post_date.month),
            #'post_day': '{0:0>2}'.format(post_date.day),
        }
        return full_reverse('comment_feed', kwargs=kwargs)

    # CUSTOM METHODS

    def allow_comments(self):
        if not self.comment_status or not self.is_published():
            return False
        limit = registry['marchena:COMMENTS_DAYS_ALLOWED']
        if not limit:
            return True
        limit = timezone.now() - timedelta(limit)
        return (self.publish_from
                    and self.publish_from >= limit
                or self.creation_date
                    and self.creation_date >= limit)
    allow_comments.boolean = True
    allow_comments.short_description = _('Allow comments?')

    def allow_pings(self):
        return (self.ping_status == True and self.is_published())
    allow_pings.boolean = True
    allow_pings.short_description = _('Allow pings?')

    def get_blog(self):
        Blog = get_model('marchena', 'Blog')
        return Blog.cache.get(self.blog_id)
    get_blog.short_description = _('Blog')

    def get_content(self):
        return mark_safe(self.content_html)
    get_content.short_description = _('Content')

    def get_excerpt(self, max_words=100, end_text='...'):
        if not self.excerpt_html:
            truncator = Truncator(self.content_html)
            excerpt = truncator.words(max_words, end_text, True)
            return mark_safe(excerpt)
        else:
            return mark_safe(self.excerpt_html)
    get_excerpt.short_description = _('Excerpt')

    def get_images(self):
        if self._images is Undefined:
            self._images = [
                img.image
                for img
                in self.images.all()
                if img.image
            ]
        return self._images

    def get_main_image(self):
        if self.get_images():
            return self.get_images()[0]
        else:
            return None

    def get_next_in_order(self, user=None, same_blog=True):
        qs = self._default_manager.published(user)
        qs = qs.filter(publish_from__gt=self.publish_from)
        if same_blog:
            qs = qs.filter(blog_id=self.blog_id)
        qs = qs.order_by('publish_from')
        return qs.first()

    def get_previous_in_order(self, user=None, same_blog=True):
        qs = self._default_manager.published(user)
        qs = qs.filter(publish_from__lt=self.publish_from)
        if same_blog:
            qs = qs.filter(blog_id=self.blog_id)
        qs = qs.order_by('-publish_from')
        return qs.first()

    def get_publish_date(self):
        return self.publish_from if self.publish_from else FakeDate(0, 0, 0)
    get_publish_date.short_description = _('Publish Date')

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('title__icontains', )


class AbstractPostImage(Orderable, Illustrated):

    post = models.ForeignKey(
            'Post',
            related_name='images',
            verbose_name=_('Post'))
    caption = models.CharField(
            max_length=127,
            blank=True,
            verbose_name=_('Caption'))

    class Meta:
        abstract = True
        folder_name = 'blog_posts'
        order_with_respect_to = 'post'
        verbose_name = _('Post Image')
        verbose_name_plural = _('Post Images')

    def get_upload_path(self, filename):
        filename = self.post.slug.replace('-', '_')
        return super(AbstractPostImage, self).get_upload_path(filename)


@python_2_unicode_compatible
class AbstractTag(Slugged):

    name = models.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Name'))
    description = models.TextField(
            blank=True,
            verbose_name=_('Description'),
            help_text=_('The description is usually not prominent.'))

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {
            #'tag_pk': self.pk,
            'tag_slug': self.slug,
        }
        return reverse('post_list', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {
            #'tag_pk': self.pk,
            'tag_slug': self.slug,
        }
        return full_reverse('post_feed', kwargs=kwargs)

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )

