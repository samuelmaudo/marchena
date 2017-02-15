# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import conditional_escape, linebreaks
from django.utils.safestring import mark_safe, SafeData
from django.utils.text import Truncator
from django.utils.translation import ugettext, ugettext_lazy as _

from yepes import fields
from yepes.apps import apps
from yepes.cache import LookupTable
from yepes.conf import settings
from yepes.model_mixins import (
    Linked,
    Logged,
    Nestable,
    Orderable,
    ParentForeignKey,
)
from yepes.types import Undefined

CommentManager = apps.get_class('comments.managers', 'CommentManager')


@python_2_unicode_compatible
class BaseComment(Nestable, Logged, Linked):

    parent = ParentForeignKey(
            'self',
            blank=True,
            null=True,
            related_name='children',
            verbose_name=_('Parent'))

    author_name = fields.CharField(
            blank=False,
            max_length=63,
            verbose_name=_('Name'))
    author_email = fields.EmailField(
            blank=False,
            max_length=63,
            verbose_name=_('Email Address'))
    author_url = models.URLField(
            blank=True,
            max_length=127,
            verbose_name=_('URL'))

    ip_address = models.GenericIPAddressField(
            blank=True,
            null=True,
            protocol='both',
            unpack_ipv4=True,
            verbose_name=_('IP Address'))
    user_agent = fields.TextField(
            blank=True,
            verbose_name=_('User Agent'))

    karma = fields.IntegerField(
            default=0,
            blank=True,
            verbose_name=_('Karma'))
    status = fields.CachedForeignKey(
            'CommentStatus',
            on_delete=models.PROTECT,
            related_name='comments',
            verbose_name=_('Status'))
    is_published = fields.BooleanField(
            editable=False,
            default=True,
            verbose_name=_('Is Published?'))

    objects = CommentManager()

    class Meta:
        abstract = True
        index_together = [('status', 'creation_date')]
        ordering = ['-creation_date']
        permissions = [('can_moderate', _('Can moderate comments'))]
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    _author_email = Undefined
    _author_name = Undefined

    def __init__(self, *args, **kwargs):
        super(BaseComment, self).__init__(*args, **kwargs)
        self.old_status_id = self.status_id

    def __str__(self):
        args = (
            self.pk,
            self.get_author_name(),
        )
        return '#{0} {1}'.format(*args)

    def save(self, **kwargs):
        updated_fields = kwargs.get('update_fields', ())
        new_record = (kwargs.get('force_insert', False)
                      or not (self.pk or updated_fields))

        if (not updated_fields
                and (new_record or self.status_id != self.old_status_id)):
            status = self.get_status()
            self.is_published = status.publish_comment
            self.old_status_id = status.id

        self._author_email = Undefined
        self._author_name = Undefined
        super(BaseComment, self).save(**kwargs)

    def get_absolute_url(self):
        if not hasattr(self, 'post'):
            msg = ('{cls} is missing a post. Define {cls}.post, or override '
                   '{cls}.get_absolute_url().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))
        else:
            return '#'.join((self.post.get_absolute_url(), self.get_anchor()))

    # CUSTOM METHODS

    def get_anchor(self):
        return settings.COMMENT_ANCHOR_PATTERN.format(**self.get_anchor_data())

    def get_anchor_data(self):
        data = {
            'id': self.id,
            'parent_id': self.parent_id,
        }
        if hasattr(self, 'post_id'):
            data['post_id'] = self.post_id
        elif hasattr(self, 'post'):
            data['post_id'] = self.post.pk

        return data

    def get_author_email(self):
        if self._author_email is Undefined:
            if not hasattr(self, 'author') or self.author is None:
                self._author_email = self.author_email
            else:
                self._author_email = self.author.email

        return self._author_email
    get_author_email.short_description = _('Email Address')

    def get_author_link(self):
        url = self.get_author_url()
        name = conditional_escape(self.get_author_name())
        if url:
            return mark_safe('<a href="{0}" rel="nofollow">{1}</a>'.format(url, name))
        else:
            return mark_safe(name)
    get_author_link.short_description = _('Author')

    def get_author_name(self):
        if self._author_name is Undefined:
            if not hasattr(self, 'author') or self.author is None:
                self._author_name = self.author_name
            else:
                self._author_name = (self.author.get_full_name()
                                     or self.author.get_username())
        return self._author_name
    get_author_name.short_description = _('Name')

    def get_author_url(self):
        return self.author_url
    get_author_url.short_description = _('URL')

    def get_children(self, limit=None, status=None, order_by=None):
        qs = self.children.all()
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
        status = self.get_status()
        if status.comment_replacement:
            return mark_safe(status.comment_replacement)
        elif hasattr(self, 'content_html'):
            return mark_safe(self.content_html)
        elif hasattr(self, 'content'):
            return mark_safe(linebreaks(self.content, autoescape=True))
        else:
            msg = ('{cls} is missing a content. Define {cls}.content_html, '
                   '{cls}.content, or override {cls}.get_content().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))
    get_content.short_description = _('Content')

    def get_date(self):
        return self.creation_date
    get_date.short_description = _('Date')

    def get_excerpt(self, max_words=20, end_text='...'):
        content = self.get_content()
        if hasattr(content, '__html__'):
            # The __html__ attribute means the content was previously
            # marked as safe, so can include HTML tags.
            truncator = Truncator(content.__html__())
            if end_text == '...':
                end_text = '&hellip;'

            return mark_safe(truncator.words(max_words, end_text, html=True))
        else:
            return Truncator(content).words(max_words, end_text, html=False)
    get_excerpt.short_description = _('Excerpt')

    def get_link(self):
        url = self.get_absolute_url()
        text = ugettext('{author} on {post}').format(**{
            'author': self.get_author_name(),
            'post': self.get_post(),
        })
        return mark_safe('<a href="{0}">{1}</a>'.format(url, escape(text)))

    def get_status(self):
        return self.status
    get_excerpt.short_description = _('Status')


class AbstractComment(BaseComment):

    post = models.ForeignKey(
            'posts.Post',
            related_name='comments',
            verbose_name=_('Post'))

    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            blank=True,
            null=True,
            related_name='comments',
            verbose_name=_('Author'))

    content = fields.RichTextField(
            verbose_name=_('Comment'))

    search_fields = {'content': 1}

    class Meta:
        abstract = True


@python_2_unicode_compatible
class AbstractCommentStatus(Orderable):

    label = fields.CharField(
            max_length=63,
            verbose_name=_('Label'))
    api_id = fields.IdentifierField(
            unique=True,
            verbose_name=_('API Id'),
            help_text=_('This field is for internally identify the comment status. '
                        'Can only contain lowercase letters, numbers and underscores.'))
    color = fields.ColorField(
            verbose_name=_('Color'),
            help_text=_('This color is used on the admin site for visually '
                        'identify the comment status.'))

    publish_comment = fields.BooleanField(
            default=True,
            verbose_name=_('Publishes Comments'),
            help_text=_('Uncheck this box to make the comments effectively '
                        'disappear from the blog.'))
    comment_replacement = fields.TextField(
            blank=True,
            verbose_name=_('Comment Replacement'),
            help_text=_('The content of this field will replace the text of '
                        'the user comments. E.g.: "Inappropriate comment."'))

    objects = models.Manager()
    cache = LookupTable(
            indexed_fields=['api_id'],
            default_registry_key='comments:INITIAL_STATUS')

    class Meta:
        abstract = True
        verbose_name = _('Comment Status')
        verbose_name_plural = _('Comment Statuses')

    def __str__(self):
        return self.label

    def save(self, **kwargs):
        super(AbstractCommentStatus, self).save(**kwargs)
        self.comments.update(is_published=self.publish_comment)

    def natural_key(self):
        return (self.api_id, )

    # CUSTOM METHODS

    def replace_comment(self):
        return bool(self.comment_replacement)
    replace_comment.admin_order_field = 'comment_replacement'
    replace_comment.boolean = True
    replace_comment.short_description = _('Replaces Comments')

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('label__icontains', 'api_id__icontains')

