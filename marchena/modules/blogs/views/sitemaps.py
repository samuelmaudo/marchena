# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.sitemaps.views import SitemapView
from yepes.loading import get_class

BlogSitemap = get_class('blogs.sitemaps', 'BlogSitemap')


class BlogSitemapView(SitemapView):
    sitemap_class = BlogSitemap

