# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.conf import settings
from yepes.views import ListView

from marchena.modules.blogs.view_mixins import BlogMixin
from marchena.modules.links.view_mixins import LinkCategoryMixin

Link = apps.get_model('links', 'Link')
LinkCategory = apps.get_model('links', 'LinkCategory')


class LinksOpmlView(BlogMixin, LinkCategoryMixin, ListView):

    content_type = 'application/xml'
    link_category_field = 'pk'
    model = LinkCategory
    require_blog = settings.BLOG_MULTIPLE
    require_link_category = False
    template_name = 'links_opml.xml'

    def get_queryset(self):
        qs = super(LinksOpmlView, self).get_queryset()
        qs = qs.prefetch_related('links')
        return qs

