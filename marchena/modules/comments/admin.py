# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.html import format_html
from django.utils.six.moves.urllib.parse import urljoin
from django.utils.translation import (
    ugettext,
    ugettext_lazy as _,
)

from yepes import admin
from yepes.apps import apps
from yepes.conf import settings

from marchena.admin import BlogModelAdmin

Comment = apps.get_model('comments', 'Comment')
CommentStatus = apps.get_model('comments', 'CommentStatus')


class CommentMixin(object):

    blog_field = 'post__blog'

    date_hierarchy = 'creation_date'
    fieldsets = [
        (None, {
            'fields': [
                'status',
                'content',
            ],
        }),
        (_('Author'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'get_author_name',
                'get_author_email',
                'get_author_url',
            ]
        }),
        (_('Information'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'creation_date',
                'ip_address',
                'user_agent',
            ]
        }),
    ]
    list_display = [
        'admin_id',
        'admin_author',
        'admin_content',
        'admin_status',
        'admin_post',
    ]
    list_filter = [
        'status',
        'is_published',
    ]
    ordering = [
        '-creation_date',
    ]
    readonly_fields = [
        'creation_date',
        'get_author_email',
        'get_author_name',
        'get_author_url',
        'ip_address',
        'user_agent',
    ]
    search_fields = ['content']

    def admin_author(self, obj):

        if obj.author_id is None:
            name = format_html(
                '<a href="?author_name__exact={0}" style="color:#444"><strong>{0}</strong></a>',
                obj.get_author_name())
        else:
            name = format_html(
                '<a href="?author__id__exact={0}" style="color:#444"><strong>{1}</strong></a> <img src="{2}" alt="({3})">',
                obj.author_id,
                obj.get_author_name(),
                urljoin(settings.STATIC_URL, 'admin/img/icon-yes.gif'),
                ugettext('Authenticated'))

        email = format_html(
            '<a href="?author_email__exact={0}" style="color:#444">{0}</a>',
            obj.get_author_email())

        ip_address = format_html(
            '<a href="?ip_address__exact={0}" style="color:#444">{0}</a>',
            obj.ip_address)

        return '<br>'.join((name, email, ip_address))
    admin_author.admin_order_field = 'author_name'
    admin_author.allow_tags = True
    admin_author.short_description = _('Author')

    def admin_content(self, obj):
        creation_date = ugettext('Submitted on {date:%Y/%m/%d at %I:%M %p}')
        return format_html(
            '<p style="color:#999">{0}</p>{1}',
            creation_date.format(date=obj.creation_date),
            obj.get_excerpt())
    admin_content.allow_tags = True
    admin_content.short_description = _('Content')

    def admin_id(self, obj):
        return '#{0}'.format(obj.pk)
    admin_id.admin_order_field = 'pk'
    admin_id.short_description = _('Comment')

    def admin_post(self, obj):
        post = format_html(
            '<a href="?post__id__exact={0}" style="color:#444">{1}</a>',
            obj.post_id,
            obj.post,)

        view_link = format_html(
            '<a href="{0}">{1}</a>',
            obj.get_absolute_url(),
            ugettext('View Post'))

        return '<br>'.join((post, view_link))
    admin_post.admin_order_field = 'post'
    admin_post.allow_tags = True
    admin_post.short_description = _('In Response To')

    def admin_status(self, obj):
        return format_html(
                '<a href="?status__id__exact={0}" style="color:{2}">{1}</a>',
                obj.status_id,
                obj.status,
                obj.status.color)
    admin_status.admin_order_field = 'status__name'
    admin_status.allow_tags = True
    admin_status.short_description = _('Status')

    def get_queryset(self, request):
        qs = super(CommentMixin, self).get_queryset(request)
        qs = qs.prefetch_related('post', 'author')
        return qs

    def _has_add_permission(self, request):
        return False

class CommentAdmin(CommentMixin, BlogModelAdmin):
    pass


class CommentStatusAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                ('label', 'publish_comment'),
                'api_id',
                'color',
                'comment_replacement',
            ],
        }),
    ]
    list_display = [
        'label',
        'admin_api_id',
        'publish_comment',
        'replace_comment',
        'index',
    ]
    list_editable = [
        'index',
    ]
    search_fields = [
        'label',
        'api_id',
    ]

    def admin_api_id(self, obj):
        return format_html(
                '<span style="background:{1};border-radius:4px;color:#f8f8ff;padding:4px 7px">{0}</span>',
                obj.api_id,
                obj.color)
    admin_api_id.admin_order_field = 'api_id'
    admin_api_id.allow_tags = True
    admin_api_id.short_description = _('API Id')


admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentStatus, CommentStatusAdmin)
