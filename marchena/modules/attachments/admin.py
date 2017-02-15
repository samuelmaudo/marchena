# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Count
from django.utils.html import escape, format_html
from django.utils.translation import ugettext, ugettext_lazy as _

from yepes import admin
from yepes.apps import apps
from yepes.contrib.thumbnails.proxies import ConfigurationProxy

Attachment = apps.get_model('attachments', 'Attachment')
AttachmentCategory = apps.get_model('attachments', 'AttachmentCategory')


class AttachmentAdmin(admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  ['category'],
        'm2m': [],
    }
    fieldsets = [
        (None, {
            'fields': [
                'title',
                'guid',
            ],
        }),
        (None, {
            'fields': [
                'file',
                'external_file',
            ],
        }),
        (None, {
            'fields': [
                'caption',
                'alt',
                'description',
                'category',
            ],
        }),
        (_('File Info'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'get_display_size',
                'mime_type',
                'width',
                'height',
            ],
        }),
        (_('Tags'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'admin_audio_tag',
                'admin_iframe_tag',
                'admin_image_tag',
                'admin_file_link',
                'admin_video_tag',
            ],
        }),
    ]
    list_display = [
        'admin_thumbnail',
        'admin_title',
        'get_display_size',
        'width',
        'height',
        'admin_category',
    ]
    list_display_links = ['admin_thumbnail', 'admin_title']
    list_filter = ['category']
    raw_id_fields = ['category']
    readonly_fields = [
        'guid',
        'get_display_size',
        'mime_type',
        'width',
        'height',
        'admin_audio_tag',
        'admin_iframe_tag',
        'admin_image_tag',
        'admin_file_link',
        'admin_video_tag',
    ]
    search_fields = ['title', 'file', 'external_file']

    def admin_audio_tag(self, obj):
        return '[audio]{0}[/audio]'.format(obj.guid)
    admin_audio_tag.short_description = _('Audio')

    def admin_category(self, obj):
        if obj.category_id is not None:
            return format_html('<a href="?category__id__exact={0}">{1}</a>',
                               obj.category_id,
                               obj.category)
        else:
            return format_html('<a href="?category__isnull=True" style="color:#444">{0}</a>',
                               ugettext('No category'))
    admin_category.admin_order_field = 'category'
    admin_category.allow_tags = True
    admin_category.short_description = _('category')

    def admin_file_link(self, obj):
        return '[link]{0}[/link]'.format(obj.guid)
    admin_file_link.short_description = _('Link')

    def admin_iframe_tag(self, obj):
        return '[iframe]{0}[/iframe]'.format(obj.guid)
    admin_iframe_tag.short_description = _('IFrame')

    def admin_image_tag(self, obj):
        return '[image]{0}[/image]'.format(obj.guid)
    admin_image_tag.short_description = _('Image')

    def admin_video_tag(self, obj):
        return '[video]{0}[/video]'.format(obj.guid)
    admin_video_tag.short_description = _('Video')

    def admin_thumbnail(self, obj):
        if not obj.is_image:
            return ''

        config = ConfigurationProxy(60, 60, mode='fill')
        try:
            thumb = obj.image.get_thumbnail(config)
        except IOError:
            return ''

        return thumb.get_tag(style='border: 1px solid #e0e0e0')
    admin_thumbnail.allow_tags = True
    admin_thumbnail.short_description = ''

    def admin_title(self, obj):
        return format_html(
            '<strong>{0}</strong><br><span style="color:#444">{1}</span>',
            obj.title,
            obj.get_file_name())
    admin_title.admin_order_field = 'title'
    admin_title.allow_tags = True
    admin_title.short_description = _('File')

    def get_queryset(self, request):
        qs = super(AttachmentAdmin, self).get_queryset(request)
        return qs.prefetch_related('category')


class AttachmentCategoryAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'name',
                'description',
            ],
        }),
    ]
    list_display = [
        'name',
        'description',
        'admin_attachment_count',
    ]
    search_fields = ['name']

    def admin_attachment_count(self, obj):
        return obj.attachment_count
    admin_attachment_count.admin_order_field = 'attachment_count'
    admin_attachment_count.short_description = _('Attachments')

    def get_queryset(self, request):
        qs = super(AttachmentCategoryAdmin, self).get_queryset(request)
        qs = qs.annotate(attachment_count=Count('attachments'))
        return qs


admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(AttachmentCategory, AttachmentCategoryAdmin)
