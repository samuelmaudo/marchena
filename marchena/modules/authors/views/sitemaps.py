# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.sitemaps.views import SitemapView
from yepes.loading import get_class

AuthorSitemap = get_class('authors.sitemaps', 'AuthorSitemap')


class AuthorSitemapView(SitemapView):
    sitemap_class = AuthorSitemap

