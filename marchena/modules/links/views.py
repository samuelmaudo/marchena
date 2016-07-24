# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.views import ListView

Link = apps.get_model('links', 'Link')
LinkCategory = apps.get_model('links', 'LinkCategory')

BlogMixin = apps.get_class('marchena.view_mixins', 'BlogMixin')
LinkCategoryMixin = apps.get_class('links.view_mixins', 'LinkCategoryMixin')


class LinkListView(BlogMixin, ListView):
    """
    Displays a list of links.
    """
    model = Link
    require_blog = True


class LinkCategoryDetailView(LinkCategoryMixin, LinkListView):
    """
    Displays a list of links that belong to the given category.
    """
    require_link_category = True


class LinkCategoryListView(BlogMixin, ListView):
    """
    Displays a list of links.
    """
    model = LinkCategory
    prefetch_links = False
    require_blog = True

    def get_queryset(self):
        qs = super(LinksOpmlView, self).get_queryset()
        if self.prefetch_links:
            qs = qs.prefetch_related('links')
        return qs


class LinksOpmlView(BlogMixin, LinkCategoryMixin, ListView):

    content_type = 'application/xml'
    link_category_field = 'pk'
    model = LinkCategory
    require_blog = True
    require_link_category = False
    template_name = 'links_opml.xml'

    def get_queryset(self):
        qs = super(LinksOpmlView, self).get_queryset()
        qs = qs.prefetch_related('links')
        return qs

