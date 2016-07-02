# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.views import ListView

BlogMixin = apps.get_class('blogs.view_mixins', 'BlogMixin')
LinkCategoryMixin = apps.get_class('links.view_mixins', 'LinkCategoryMixin')

Link = apps.get_model('links', 'Link')
LinkCategory = apps.get_model('links', 'LinkCategory')


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
    require_blog = True

