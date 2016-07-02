# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from yepes import admin
from yepes.apps import apps

Blog = apps.get_model('blogs', 'Blog')


class BlogAdmin(admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  [],
        'm2m': ['authors'],
    }
    fieldsets = [
        (None, {
            'fields': [
                'title',
                'subtitle',
                'description',
                'authors'
            ],
        }),
        (_('Metadata'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'meta_title',
                'slug',
                'meta_description',
                'meta_keywords',
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
    list_display = ['title', 'subtitle', 'admin_authors']
    prepopulated_fields = {'slug': ('title', )}
    raw_id_fields = ['authors']
    search_fields = ['title', 'subtitle']

    def admin_authors(self, obj):
        links = [
            format_html('<a href="?authors__id__exact={0}">{1}</a>',
                        user.pk,
                        user.get_full_name() or user.get_username())
            for user
            in obj.authors.all()
        ]
        return ', '.join(links) if links else _('No authors')
    admin_authors.allow_tags = True
    admin_authors.short_description = _('Authors')

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(BlogAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'authors':
            formfield.initial = [kwargs['request'].user]
        return formfield

    def get_queryset(self, request):
        qs = super(BlogAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(authors=request.user)
        return qs


admin.site.register(Blog, BlogAdmin)
