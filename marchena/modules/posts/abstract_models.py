# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from collections import namedtuple
from datetime import timedelta
from string import punctuation

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F, Q
from django.db.models.query import QuerySet
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
from yepes.apps import apps
from yepes.conf import settings
from yepes.contrib.registry import registry
from yepes.loading import LazyModel
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

from marchena.modules.attachments.processors import attachment_tags

PostManager = apps.get_class('posts.managers', 'PostManager')
PostRecordManager = apps.get_class('posts.managers', 'PostRecordManager')

PostRecord = LazyModel('posts', 'PostRecord')

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
    description = fields.TextField(
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
        kwargs = {'category_slug': self.slug}
        if settings.BLOG_MULTIPLE:
            kwargs['blog_slug'] = self.blog.slug
        return reverse('post_list', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {'category_slug': self.slug}
        if settings.BLOG_MULTIPLE:
            kwargs['blog_slug'] = self.blog.slug
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
            processors=[attachment_tags],
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

    comment_status = fields.BooleanField(
            default=lambda: registry['posts:ALLOW_COMMENTS'],
            verbose_name=_('Allow comments on this post'))
    ping_status = fields.BooleanField(
            default=True,
            verbose_name=_('Allow trackbacks and pingbacks to this post'))

    views_count = models.PositiveIntegerField(
            default=0,
            blank=True,
            editable=False,
            db_index=True,
            verbose_name=_('Views'))
    comment_count = models.PositiveIntegerField(
            default=0,
            blank=True,
            editable=False,
            db_index=True,
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

    objects = PostManager()

    search_fields = {'title': 5, 'subtitle': 3, 'content': 1}

    class Meta:
        abstract = True
        folder_name = 'blog_posts'
        index_together = [
            ('publish_status', 'creation_date'),
        ]
        ordering = ['-publish_from']
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        kwargs = {
            'post_slug': self.slug,
            'post_guid': self.guid,
        }
        if settings.BLOG_MULTIPLE:
            kwargs['blog_slug'] = self.blog.slug

        return reverse('post_detail', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {
            'post_slug': self.slug,
            'post_guid': self.guid,
        }
        if settings.BLOG_MULTIPLE:
            kwargs['blog_slug'] = self.blog.slug

        return full_reverse('comment_feed', kwargs=kwargs)

    # CUSTOM METHODS

    def allow_comments(self):
        if not self.comment_status or not self.is_published():
            return False
        limit = registry['comments:MAX_DAYS']
        if not limit:
            return True
        limit = timezone.now() - timedelta(limit)
        if self.publish_from:
            return (self.publish_from >= limit)
        elif self.creation_date:
            return (self.creation_date >= limit)
        else:
            return False
    allow_comments.boolean = True
    allow_comments.short_description = _('Allow comments?')

    def allow_pings(self):
        return (self.ping_status == True and self.is_published())
    allow_pings.boolean = True
    allow_pings.short_description = _('Allow pings?')

    def get_comments(self, limit=None, status=None, order_by=None):
        qs = self.comments.all()
        qs = qs.prefetch_related('author')
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

    def get_excerpt(self, max_words=55, end_text='...'):
        if not self.excerpt_html:
            truncator = Truncator(self.content_html)
            if end_text == '...':
                end_text = '&hellip;'
            return mark_safe(truncator.words(max_words, end_text, html=True))
        else:
            return mark_safe(self.excerpt_html)
    get_excerpt.short_description = _('Excerpt')

    def get_next_in_order(self, user=None, same_blog=True):
        qs = self.__class__._default_manager.published(user)
        qs = qs.filter(publish_from__gt=self.publish_from)
        if same_blog:
            qs = qs.filter(blog_id=self.blog_id)
        qs = qs.order_by('publish_from')
        return qs.first()

    def get_previous_in_order(self, user=None, same_blog=True):
        qs = self.__class__._default_manager.published(user)
        qs = qs.filter(publish_from__lt=self.publish_from)
        if same_blog:
            qs = qs.filter(blog_id=self.blog_id)
        qs = qs.order_by('-publish_from')
        return qs.first()

    def get_publish_date(self):
        return self.publish_from if self.publish_from else FakeDate(0, 0, 0)
    get_publish_date.short_description = _('Publish Date')

    def get_related_posts(self, limit=5, same_blog=True):
        manager = self.__class__._default_manager
        qs = manager.published().exclude(pk__exact=self.pk)
        if same_blog:
            qs = qs.filter(blog_id=self.blog_id)

        def get_primary_keys(posts):
            if isinstance(posts, QuerySet):
                return list(posts.values_list('pk', flat=True))
            else:
                return [post.pk for post in posts]

        # Search similar posts using the post's title.
        query = ' '.join([
            term
            for term
            in [
                term.strip(punctuation)    # This transforms
                for term                   # "Super toy: pack 10 u."
                in self.title.split()       # into
                if not term.endswith('.')  # "Super toy pack"
            ]
            if not term.isdigit()
        ])
        related_post_ids = get_primary_keys(list(
            qs.search(
                query
            )[:limit]
        ))
        remaining = limit - len(related_post_ids)

        if remaining > 0:
            # Fetch post from post's categories.
            related_post_ids += get_primary_keys(
                qs.filter(
                    categories__in=self.categories.all()
                ).exclude(
                    pk__in=related_post_ids
                ).distinct(   # Call to `distinct()` is required
                ).order_by(   # because `categories__in` filter
                    '-score'  # may result in duplicates.
                )[:remaining]
            )
            remaining = limit - len(related_post_ids)

            if remaining > 0:
                # Fetch post from the rest of the blog.
                related_post_ids += get_primary_keys(
                    qs.exclude(
                        pk__in=related_post_ids
                    ).order_by(
                        '-score'
                    )[:remaining]
                )
                remaining = limit - len(related_post_ids)

        related_posts = manager.filter(
            pk__in=related_post_ids
        ).order_by(
            '-score'
        )
        return related_posts

    def increase_comment_count(self):
        record, _ = PostRecord.objects.get_or_create(post=self)
        record.comment_count = F('comment_count') + 1
        record.save(update_fields=['comment_count'])

    def increase_ping_count(self):
        record, _ = PostRecord.objects.get_or_create(post=self)
        record.ping_count = F('ping_count') + 1
        record.save(update_fields=['ping_count'])

    def increase_views_count(self):
        record, _ = PostRecord.objects.get_or_create(post=self)
        record.views_count = F('views_count') + 1
        record.save(update_fields=['views_count'])

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
            verbose_name=_('Score'))

    objects = PostRecordManager()

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
    description = fields.TextField(
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
        kwargs = {'tag_slug': self.slug}
        return reverse('post_list', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {'tag_slug': self.slug}
        return full_reverse('post_feed', kwargs=kwargs)

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )

