# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from yepes import admin
from yepes.apps import apps

from marchena.admin import BlogModelAdmin

Link = apps.get_model('links', 'Link')
LinkCategory = apps.get_model('links', 'LinkCategory')


class LinkMixin(object):

    autocomplete_lookup_fields = {
        'fk':  ['blog', 'category'],
        'm2m': [],
    }
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'url',
                'description',
                'category',
            ],
        }),
        (_('Blog'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'blog',
            ]
        }),
        (_('Image'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'image',
            ],
        }),
    ]
    list_display = ['name', 'url', 'admin_category']
    list_filter = ['blog', 'category']
    raw_id_fields = ['blog', 'category']
    search_fields = ['name', 'url']

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

    def get_queryset(self, request):
        qs = super(LinkMixin, self).get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(blog__authors=request.user)
        return qs.prefetch_related('category')

class LinkAdmin(LinkMixin, BlogModelAdmin):
    pass


class LinkCategoryMixin(object):

    autocomplete_lookup_fields = {
        'fk':  ['blog'],
        'm2m': [],
    }
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'description',
            ],
        }),
        (_('Blog'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'blog',
            ]
        }),
        (_('Metadata'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'slug',
            ]
        }),
    ]
    list_display = ['name', 'description', 'slug', 'admin_link_count']
    prepopulated_fields = {'slug': ('name', )}
    raw_id_fields = ['blog']
    search_fields = ['name']

    def admin_link_count(self, obj):
        return obj.link_count
    admin_link_count.admin_order_field = 'link_count'
    admin_link_count.short_description = _('Links')

    def get_queryset(self, request):
        qs = super(LinkCategoryMixin, self).get_queryset(request)
        qs = qs.annotate(link_count=Count('links'))
        if not request.user.is_superuser:
            qs = qs.filter(blog__authors=request.user)
        return qs

class LinkCategoryAdmin(LinkCategoryMixin, BlogModelAdmin):
    pass


admin.site.register(Link, LinkAdmin)
admin.site.register(LinkCategory, LinkCategoryAdmin)
