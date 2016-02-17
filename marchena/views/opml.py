# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.loading import get_model
from yepes.views import ListView

from marchena.view_mixins import BlogMixin, LinkCategoryMixin

Link = get_model('marchena', 'Link')
LinkCategory = get_model('marchena', 'LinkCategory')


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

