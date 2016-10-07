# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.conf import settings
from yepes.view_mixins import CanonicalMixin
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
    require_blog = False


class LinkCategoryDetailView(LinkCategoryMixin, CanonicalMixin, LinkListView):
    """
    Displays a list of links that belong to the given category.
    """
    require_blog = settings.BLOG_MULTIPLE
    require_link_category = True

    def get_canonical_path(self, request):
        category = self.get_link_category()
        return category.get_absolute_url()

    def get_template_names(self):
        names = super(LinkCategoryDetailView, self).get_template_names()
        category = self.get_link_category()
        if category is not None:
            names.insert(-1, '{0}/{1}_detail.html'.format(
                category._meta.app_label,
                category._meta.model_name,
            ))
        return names


class LinkCategoryListView(BlogMixin, ListView):
    """
    Displays a list of links.
    """
    model = LinkCategory
    require_blog = settings.BLOG_MULTIPLE

