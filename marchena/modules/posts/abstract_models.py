# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from collections import namedtuple
from datetime import timedelta

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F, Q
from django.utils import six
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.translation import (
    ugettext,
    ugettext_lazy as _,
)

from yepes import fields
from yepes.contrib.registry import registry
from yepes.model_mixins import (
    Displayable,
    Illustrated,
    Logged,
    MetaData,
    Orderable,
    Slugged,
)
from yepes.types import Undefined
from yepes.urlresolvers import full_reverse

FakeDate = namedtuple('FakeDate', 'year, month, day')


@python_2_unicode_compatible
class AbstractCategory(Illustrated, Slugged, MetaData):

    blog = fields.CachedForeignKey(
            'blogs.Blog',
            related_name='categories',
            verbose_name=_('Blog'))
    name = fields.CharField(
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
            #'blog_pk': self.blog.pk,
            'blog_slug': self.blog.slug,
            #'category_pk': self.pk,
            'category_slug': self.slug,
        }
        return reverse('post_list', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {
            #'blog_pk': self.blog.pk,
            'blog_slug': self.blog.slug,
            #'category_pk': self.pk,
            'category_slug': self.slug,
        }
        return full_reverse('post_feed', kwargs=kwargs)

    def get_upload_path(self, filename):
        filename = self.slug.replace('-', '_')
        return super(AbstractCategory, self).get_upload_path(filename)

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )


@python_2_unicode_compatible
class AbstractPost(Illustrated, Displayable, Logged):

    blog = fields.CachedForeignKey(
            'blogs.Blog',
            related_name='posts',
            verbose_name=_('Blog'))
    guid = fields.GuidField(
            editable=False,
            verbose_name=_('Global Unique Identifier'))
    title = fields.CharField(
            max_length=255,
            verbose_name=_('Title'))
    subtitle = fields.CharField(
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
            'authors.Author',
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
    ping_status = models.BooleanField(
            default=True,
            verbose_name=_('Allow trackbacks and pingbacks to this post'))

    search_fields = {'title': 5, 'content': 1}

    class Meta:
        abstract = True
        folder_name = 'blog_posts'
        ordering = ['-publish_from']
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        #post_date = self.get_publish_date()
        kwargs = {
            #'blog_pk': self.blog.pk,
            'blog_slug': self.blog.slug,
            #'post_pk': self.pk,
            'post_guid': self.guid,
            'post_slug': self.slug,
            #'post_year': '{0:0>4}'.format(post_date.year),
            #'post_month': '{0:0>2}'.format(post_date.month),
            #'post_day': '{0:0>2}'.format(post_date.day),
        }
        return reverse('post_detail', kwargs=kwargs)

    def get_feed_url(self):
        #post_date = self.get_publish_date()
        kwargs = {
            #'blog_pk': self.blog.pk,
            'blog_slug': self.blog.slug,
            #'post_pk': self.pk,
            'post_guid': self.guid,
            'post_slug': self.slug,
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

    def get_comments(self, limit=None, status=None, order_by=None):
        qs = self.comments.all()
        if status is None:
            qs = qs.published()
        elif isinstance(status, six.string_types):
            qs = qs.filter(status__api_id=status)
        else:
            qs = qs.filter(status=status)
        if order_by is None:
            qs = qs.order_by('-creation_date')
        else:
            qs = qs.order_by(order_by)
        if limit:
            qs = qs[:limit]
        return qs

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


@python_2_unicode_compatible
class AbstractPostRecord(models.Model):

    post = models.OneToOneField(
            'Post',
            related_name='stats',
            verbose_name=_('Post'))

    views_count = models.PositiveIntegerField(
            default=0,
            blank=True,
            editable=False,
            verbose_name=_('Views'))
    comment_count = models.PositiveIntegerField(
            default=0,
            blank=True,
            editable=False,
            verbose_name=_('Comments'))
    ping_count = models.PositiveIntegerField(
            default=0,
            blank=True,
            editable=False,
            verbose_name=_('Pings'))

    score = models.PositiveIntegerField(
            default=0,
            blank=True,
            editable=False,
            db_index=True,
            verbose_name=_('Score'))

    class Meta:
        abstract = True
        ordering = ['-score']
        verbose_name = _('Post Record')
        verbose_name_plural = _('Post Records')

    def __str__(self):
        return ugettext('Record for {post}').format(post=self.post)


@python_2_unicode_compatible
class AbstractTag(Slugged):

    name = fields.CharField(
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

