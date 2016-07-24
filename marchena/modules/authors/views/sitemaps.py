# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.contrib.sitemaps.views import SitemapView

AuthorSitemap = apps.get_class('authors.sitemaps', 'AuthorSitemap')


class AuthorSitemapView(SitemapView):
    sitemap_class = AuthorSitemap

