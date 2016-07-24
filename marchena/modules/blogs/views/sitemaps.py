# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.contrib.sitemaps.views import SitemapView

BlogSitemap = apps.get_class('blogs.sitemaps', 'BlogSitemap')


class BlogSitemapView(SitemapView):
    sitemap_class = BlogSitemap

