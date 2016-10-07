# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

import os.path
import mimetypes

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.formats import number_format
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.apps import apps
from yepes.conf import settings
from yepes.model_mixins import Calculated, Logged
from yepes.utils import slugify
from yepes.utils.html import make_double_tag, make_single_tag
from yepes.utils.properties import cached_property

SourceFile = apps.get_class('thumbnails.files', 'SourceFile')


def file_upload_to(instance, filename):
    return instance.get_upload_path(filename)


@python_2_unicode_compatible
class AbstractAttachment(Logged, Calculated):

    guid = fields.GuidField(
            editable=False,
            verbose_name=_('Global Unique Identifier'))

    title = fields.CharField(
            max_length=63,
            verbose_name=_('Title'))
    caption = fields.CharField(
            max_length=255,
            blank=True,
            verbose_name=_('Caption'))
    alt = fields.CharField(
            max_length=127,
            blank=True,
            verbose_name=_('Alternate Text'))
    description = fields.TextField(
            blank=True,
            verbose_name=_('Description'))

    file = models.FileField(
            blank=True,
            max_length=127,
            upload_to=file_upload_to,
            verbose_name=_('File'))
    external_file = models.URLField(
            blank=True,
            max_length=127,
            verbose_name=_('External File'))

    size = fields.IntegerField(
            blank=True,
            calculated=True,
            min_value=0,
            null=True,
            verbose_name=_('Size'))
    height = fields.IntegerField(
            blank=True,
            calculated=True,
            min_value=0,
            null=True,
            verbose_name=_('Height'))
    width = fields.IntegerField(
            blank=True,
            calculated=True,
            min_value=0,
            null=True,
            verbose_name=_('Width'))

    category = models.ForeignKey(
            'AttachmentCategory',
            blank=True,
            null=True,
            on_delete=models.PROTECT,
            related_name='attachments',
            verbose_name=_('Category'))

    class Meta:
        abstract = True
        folder_name = 'attachments'
        ordering = ['title']
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    def __str__(self):
        return self.title

    def clean(self):
        super(AbstractAttachment, self).clean()
        if not self.file and not self.external_file:
            msg = _('You must upload a file or set the URL of an external file.')
            raise ValidationError({'file': msg})

    def get_upload_path(self, filename):
        if self.title:
            _, extension = os.path.splitext(filename)
            return slugify(self.title, ascii=True).replace('-', '_') + extension
        else:
            return filename

    # CUSTOM METHODS

    def calculate_height(self):
        if not self.file or not self.is_image:
            return None
        else:
            return self.image.height

    def calculate_size(self):
        if not self.file:
            return None
        else:
            return self.file.size

    def calculate_width(self):
        if not self.file or not self.is_image:
            return None
        else:
            return self.image.width

    def get_audio_tag(self, **attrs):
        attrs['src'] = self.get_file_url()
        attrs.setdefault('controls', True)
        attrs.setdefault('preload', 'none')
        content = self.get_file_link(text=(self.alt or self.title))
        return make_double_tag('audio', content, attrs)

    def get_display_size(self):
        if self.size is None:
            return ''

        bytes = self.size
        if bytes < 1024:
            return '{0} B'.format(number_format(bytes))

        kb = (bytes / 1024)
        if kb < 1024:
            return '{0} KB'.format(number_format(kb, 1))

        mb = (kb / 1024)
        if mb < 1024:
            return '{0} MB'.format(number_format(mb, 1))

        gb = (mb / 1024)
        return '{0} GB'.format(number_format(gb, 1))
    get_display_size.admin_order_field = 'size'
    get_display_size.short_description = _('Size')

    def get_file_link(self, **attrs):
        attrs['href'] = self.get_file_url()
        attrs.setdefault('download', True)
        content = attrs.pop('text', self.title)
        return make_double_tag('a', content, attrs)

    def get_file_url(self):
        if not self.file:
            return self.external_file
        else:
            return self.file.url
    get_file_url.short_description = _('File')

    def get_file_name(self):
        if not self.file:
            return self.external_file
        else:
            return self.file.name
    get_file_name.short_description = _('File')

    def get_mime_type(self):
        type, _ = mimetypes.guess_type(self.get_file_name())
        return type

    def get_tag(self, **attrs):
        if self.is_audio:
            return self.get_audio_tag(**attrs)
        if self.is_image:
            return self.get_image_tag(**attrs)
        if self.is_video:
            return self.get_video_tag(**attrs)

        if self.is_external:
            url = self.get_file_url(**attrs)
            if 'youtube' in url or 'vimeo' in url:
                return self.get_iframe_tag()

        return self.get_file_link(**attrs)

    def get_iframe_tag(self, **attrs):
        attrs['src'] = self.get_file_url()
        attrs.setdefault('width', self.width or 640)
        attrs.setdefault('height', self.height or 360)
        attrs.setdefault('frameborder', 0)
        attrs.setdefault('webkitallowfullscreen', True)
        attrs.setdefault('mozallowfullscreen', True)
        attrs.setdefault('allowfullscreen', True)
        content = self.get_file_link(text=(self.alt or self.title))
        return make_double_tag('iframe', content, attrs)

    def get_image_tag(self, **attrs):
        attrs['src'] = self.get_file_url()
        if self.width:
            attrs.setdefault('width', self.width)
        if self.height:
            attrs.setdefault('height', self.height)

        attrs.setdefault('alt', self.alt or self.title)
        return make_single_tag('img', attrs)

    def get_video_tag(self, **attrs):
        attrs['src'] = self.get_file_url()
        attrs.setdefault('width', self.width or 640)
        attrs.setdefault('height', self.height or 360)
        attrs.setdefault('controls', True)
        attrs.setdefault('preload', 'metadata')
        content = self.get_file_link(text=(self.alt or self.title))
        return make_double_tag('video', content, attrs)

    # PROPERTIES

    @cached_property
    def image(self):
        if not self.file:
            return None
        else:
            return SourceFile(self.file, self.file.name, self.file.storage)

    @cached_property
    def is_audio(self):
        file_url = self.get_file_url()
        if file_url and file_url.endswith(settings.AUDIO_EXTENSIONS):
            return True

        mime_type = self.get_mime_type()
        if mime_type and mime_type.startswith('audio'):
            return True

        return False

    @cached_property
    def is_external(self):
        return not self.file

    @cached_property
    def is_image(self):
        file_url = self.get_file_url()
        if file_url and file_url.endswith(settings.IMAGE_EXTENSIONS):
            return True

        mime_type = self.get_mime_type()
        if mime_type and mime_type.startswith('image'):
            return True

        return False

    @cached_property
    def is_video(self):
        file_url = self.get_file_url()
        if file_url and file_url.endswith(settings.VIDEO_EXTENSIONS):
            return True

        mime_type = self.get_mime_type()
        if mime_type and mime_type.startswith('video'):
            return True

        return False


@python_2_unicode_compatible
class AbstractAttachmentCategory(models.Model):

    name = fields.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Name'))
    description = fields.TextField(
            blank=True,
            verbose_name=_('Description'))

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Attachment Category')
        verbose_name_plural = _('Attachment Categories')

    def __str__(self):
        return self.name

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )

