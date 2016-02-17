# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from yepes import admin
from yepes.loading import get_model
from yepes.utils.humanize import naturalday

from marchena.admin import BlogModelAdmin

Category = get_model('posts', 'Category')
Post = get_model('posts', 'Post')
PostImage = get_model('posts', 'PostImage')
Tag = get_model('posts', 'Tag')


class CategoryMixin(object):

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
        (_('Image'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'image',
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
    ]
    list_display = ['name', 'description', 'slug', 'admin_post_count']
    prepopulated_fields = {'slug': ('name', )}
    raw_id_fields = ['blog']
    search_fields = ['name']

    def admin_post_count(self, obj):
        return obj.post_count
    admin_post_count.admin_order_field = 'post_count'
    admin_post_count.short_description = _('Posts')

    def get_queryset(self, request):
        qs = super(CategoryMixin, self).get_queryset(request)
        qs = qs.annotate(post_count=Count('posts'))
        if not request.user.is_superuser:
            qs = qs.filter(blog__authors=request.user)
        return qs

class CategoryAdmin(CategoryMixin, BlogModelAdmin):
    pass


class PostImageInline(admin.TabularInline):

    classes = ['grp-collapse', 'grp-closed']
    formfield_overrides = {
        models.PositiveIntegerField: {
            'widget': forms.HiddenInput
        },
    }
    extra = 0
    model = PostImage
    sortable_field_name = 'index'


class PostMixin(object):

    autocomplete_lookup_fields = {
        'fk':  ['blog'],
        'm2m': ['authors', 'categories', 'tags'],
    }
    date_hierarchy = 'creation_date'
    fieldsets = [
        (None, {
            'fields': [
                'title',
                'subtitle',
                'content',
                'authors',
                'categories',
                'tags',
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
                'meta_title',
                'slug',
                'meta_description',
                'meta_keywords',
            ]
        }),
        (_('Visibility'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'publish_status',
                'publish_from',
                'publish_to',
            ]
        }),
        (_('Excerpt'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'excerpt',
            ]
        }),
        (_('Discussion'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'comment_status',
                'ping_status',
            ]
        }),
    ]
    inlines = [PostImageInline]
    list_display = [
        'title',
        'admin_authors',
        'admin_categories',
        'admin_tags',
        #'stats__comment_count',
        'admin_date',
    ]
    list_filter = [
        'authors',
        'blog',
        'categories',
        'tags',
        'publish_status',
    ]
    list_select_related = True
    prepopulated_fields = {'slug': ('title', )}
    raw_id_fields = ['authors', 'blog', 'categories', 'tags']
    search_fields = ['title', 'content']

    def admin_authors(self, obj):
        links = [
            format_html('<a href="?authors__id__exact={0}">{1}</a>',
                        author.pk,
                        author)
            for author
            in obj.authors.all()
        ]
        return ', '.join(links) if links else _('No author')
    admin_authors.allow_tags = True
    admin_authors.short_description = _('Authors')

    def admin_categories(self, obj):
        links = [
            format_html('<a href="?categories__id__exact={0}">{1}</a>',
                        category.pk,
                        category)
            for category
            in obj.categories.all()
        ]
        return ', '.join(links) if links else _('No category')
    admin_categories.allow_tags = True
    admin_categories.short_description = _('Categories')

    def admin_date(self, obj):
        if obj.is_draft():
            status = _('Draft')
        elif obj.is_hidden():
            status = _('Hidden')
        elif obj.is_published():
            status = _('Published')
        elif (obj.publish_from is not None
                and obj.publish_from >= timezone.now()):
            status = _('Future post')
        else:
            status = _('Expired post')
        return format_html(
            '<abbr title="{0}">{1}</abbr><br>{2}',
            date_format(obj.publish_from, 'DATETIME_FORMAT'),
            naturalday(obj.publish_from),
            status)
    admin_date.admin_order_field = 'publish_from'
    admin_date.allow_tags = True
    admin_date.short_description = _('Date')

    def admin_tags(self, obj):
        links = [
            format_html('<a href="?tags__id__exact={0}">{1}</a>', tag.pk, tag)
            for tag
            in obj.tags.all()
        ]
        return ', '.join(links) if links else _('No tag')
    admin_tags.allow_tags = True
    admin_tags.short_description = _('Tags')

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(PostMixin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'authors':
            formfield.initial = [kwargs['request'].user]
        return formfield

    def get_queryset(self, request):
        qs = super(PostMixin, self).get_queryset(request)
        qs = qs.prefetch_related('authors', 'categories', 'tags')
        return qs

class PostAdmin(PostMixin, admin.DisplayableMixin, BlogModelAdmin):
    pass


class TagMixin(object):

    blog_field = 'posts__blog'
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'description',
            ],
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
    list_display = ['name', 'description', 'slug', 'admin_post_count']
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ['name']

    def admin_post_count(self, obj):
        return obj.post_count
    admin_post_count.admin_order_field = 'post_count'
    admin_post_count.short_description = _('Posts')

    def get_queryset(self, request):
        qs = super(TagMixin, self).get_queryset(request)
        qs = qs.annotate(post_count=Count('posts'))
        if not request.user.is_superuser:
            qs = qs.filter(blog__authors=request.user)
        return qs

class TagAdmin(TagMixin, BlogModelAdmin):
    pass


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
