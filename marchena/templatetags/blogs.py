# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.template import Library

from yepes.apps import apps
from yepes.template import AssignTag, MultipleObjectMixin, SingleObjectMixin

Blog = apps.get_model('blogs', 'Blog')

register = Library()


## {% get_blog blog_slug **options[ as variable_name] %} #######################


class GetBlogTag(SingleObjectMixin, AssignTag):

    assign_var = False
    field_name = 'slug'
    model = Blog

    def process(self, blog_slug, **options):
        qs = self.get_queryset()
        if options.get('authors'):
            qs = qs.prefetch_related('authors')

        if options.get('categories'):
            qs = qs.prefetch_related('categories')

        if options.get('links'):
            qs = qs.prefetch_related('links')

        if options.get('posts'):
            qs = qs.prefetch_related('posts')

        return self.get_object(qs, blog_slug)

register.tag('get_blog', GetBlogTag.as_tag())


## {% get_blogs *blog_slugs **options as variable_name %} ######################


class GetBlogsTag(MultipleObjectMixin, AssignTag):

    field_name = 'slug'
    model = Blog

    def process(self, *blog_slugs, **options):
        qs = self.get_queryset()
        if options.get('authors'):
            qs = qs.prefetch_related('authors')

        if options.get('categories'):
            qs = qs.prefetch_related('categories')

        if options.get('links'):
            qs = qs.prefetch_related('links')

        if options.get('posts'):
            qs = qs.prefetch_related('posts')

        return self.get_object_list(qs, blog_slugs)

register.tag('get_blogs', GetBlogsTag.as_tag())

