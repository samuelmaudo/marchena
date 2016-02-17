# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from yepes import admin
from yepes.loading import get_model

from marchena.admin import BlogModelAdmin

Comment = get_model('comments', 'Comment')
CommentStatus = get_model('comments', 'CommentStatus')


class CommentMixin(object):

    blog_field = 'post__blog'

    date_hierarchy = 'creation_date'
    fieldsets = [
        (None, {
            'fields': [
                'content',
            ],
        }),
        (_('Author'), {
            'classes': [
                'grp-collapse',
                'grp-open',
            ],
            'fields': [
                'get_author_name',
                'get_author_email',
                'get_author_url',
            ]
        }),
        (_('Status'), {
            'classes': [
                'grp-collapse',
                'grp-open',
            ],
            'fields': [
                'status',
            ],
        }),
    ]
    list_display = [
        'admin_author',
        'admin_content',
        'admin_post',
    ]
    list_filter = ['status']
    list_select_related = True
    ordering = ['-creation_date']
    readonly_fields = [
        'get_author_email',
        'get_author_name',
        'get_author_url',
    ]
    search_fields = ['content']

    def admin_author(self, obj):
        if obj.author_id is None:
            name = obj.get_author_name()
        else:
            name = format_html(
                '{0} <img src="{1}" alt="({2})">',
                obj.get_author_name(),
                urljoin(settings.STATIC_URL, 'admin/img/icon-yes.gif'),
                _('Authenticated'))
        url = obj.get_author_url()
        return format_html('{0}<br><a href="{1}">{1}</a>', name, url)
    admin_author.allow_tags = True
    admin_author.short_description = _('Author')

    def admin_content(self, obj):
        status = obj.get_status()
        color = '#42AD3F' if status.publish_comment else '#DE2121'
        return format_html(
            '{0}: <span style="color:{1}">{2}</span><br>{3}',
            _('Status'),
            color,
            status,
            obj.get_excerpt())
    admin_content.allow_tags = True
    admin_content.short_description = _('Content')

    def admin_post(self, obj):
        return format_html(
            '{0}<br><a href="{1}">{2}</a>',
            obj.post,
            obj.get_absolute_url(),
            _('View Post'))
    admin_content.allow_tags = True
    admin_content.short_description = _('Post')

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
                'comment_replacement',
            ],
        }),
    ]
    list_display = ['label', 'api_id', 'admin_comment_count', 'index']
    list_editable = ['index']
    search_fields = ['label', 'api_id']

    def admin_comment_count(self, obj):
        return obj.comment_count
    admin_comment_count.admin_order_field = 'comment_count'
    admin_comment_count.short_description = _('Comments')

    def get_queryset(self, request):
        qs = super(CommentStatusAdmin, self).get_queryset(request)
        qs = qs.annotate(comment_count=Count('comments'))
        return qs


admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentStatus, CommentStatusAdmin)
