# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.cache import LookupTable
from yepes.conf import settings
from yepes.contrib.registry import registry
from yepes.model_mixins import (
    Logged,
    Nestable,
    Orderable,
    ParentForeignKey,
)
from yepes.types import Undefined
from yepes.urlresolvers import build_full_url

from marchena.modules.comments.managers import CommentManager


@python_2_unicode_compatible
class AbstractComment(Nestable, Logged):

    post = models.ForeignKey(
            'posts.Post',
            related_name='comments',
            verbose_name=_('Post'))
    parent = ParentForeignKey(
            'self',
            null=True,
            related_name='children',
            verbose_name=_('Parent comment'))

    user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            null=True,
            related_name='comments',
            verbose_name=_('User'))
    author_name = fields.CharField(
            blank=True,
            max_length=63,
            verbose_name=_("Author's name"))
    author_email = fields.EmailField(
            blank=True,
            max_length=63,
            verbose_name=_("Author's email address"))
    author_url = models.URLField(
            blank=True,
            max_length=127,
            verbose_name=_("Author's URL"))
    ip_address = models.GenericIPAddressField(
            blank=True,
            null=True,
            protocol='both',
            unpack_ipv4=True,
            verbose_name=_('IP address'))

    karma = models.IntegerField(
            default=0,
            blank=True,
            verbose_name=_('Karma'))
    status = fields.CachedForeignKey(
            'CommentStatus',
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
        permissions = [('can_moderate', 'Can moderate comments')]
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

    label = fields.CharField(
            max_length=63,
            verbose_name=_('Label'))
    api_id = fields.IdentifierField(
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

    objects = models.Manager()
    cache = LookupTable(
            indexed_fields=['api_id'],
            default_registry_key='marchena:COMMENTS_INITIAL_STATUS')

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

