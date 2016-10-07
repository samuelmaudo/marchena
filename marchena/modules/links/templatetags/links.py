# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.template import Library

from yepes.apps import apps
from yepes.template import AssignTag, MultipleObjectMixin, SingleObjectMixin

Link = apps.get_model('links', 'Link')
LinkCategory = apps.get_model('links', 'LinkCategory')

register = Library()


## {% get_link link_id **options[ as variable_name] %} #########################


class GetLinkTag(SingleObjectMixin, AssignTag):

    field_name = 'pk'
    model = Link
    target_var = 'link'

    def process(self, link_id, **options):
        blog = self.context.get('blog')
        if not blog:
            return None

        qs = self.get_queryset()
        qs = qs.filter(blog_id=blog.pk)
        if options.get('category'):
            qs = qs.prefetch_related('category')

        return self.get_object(qs, link_id)

register.tag('get_link', GetLinkTag.as_tag())


## {% get_link_category category_slug **options[ as variable_name] %} ##########


class GetLinkCategoryTag(SingleObjectMixin, AssignTag):

    field_name = 'slug'
    model = LinkCategory
    target_var = 'link_category'

    def process(self, category_slug, **options):
        blog = self.context.get('blog')
        if not blog:
            return None

        qs = self.get_queryset()
        qs = qs.filter(blog_id=blog.pk)
        if options.get('links'):
            qs = qs.prefetch_related('links')

        return self.get_object(qs, category_slug)

register.tag('get_link_category', GetLinkCategoryTag.as_tag())


## {% get_link_categories *category_slugs **options[ as variable_name] %} ######


class GetLinkCategoriesTag(MultipleObjectMixin, AssignTag):

    field_name = 'slug'
    model = LinkCategory
    target_var = 'link_category_list'

    def process(self, *category_slugs, **options):
        blog = self.context.get('blog')
        if not blog:
            return []

        qs = self.get_queryset()
        qs = qs.filter(blog_id=blog.pk)
        if options.get('links'):
            qs = qs.prefetch_related('links')

        return self.get_object_list(qs, category_slugs)

register.tag('get_link_categories', GetLinkCategoriesTag.as_tag())


## {% get_links *link_ids **options[ as variable_name] %} ######################


class GetLinksTag(MultipleObjectMixin, AssignTag):

    field_name = 'pk'
    model = Link
    target_var = 'link_list'

    def process(self, *link_ids, **options):
        blog = self.context.get('blog')
        if not blog:
            return []

        qs = self.get_queryset()
        qs = qs.filter(blog_id=blog.pk)
        if options.get('category'):
            qs = qs.prefetch_related('category')

        return self.get_object_list(qs, link_ids)

register.tag('get_links', GetLinksTag.as_tag())

