# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from django.utils import timezone

from yepes.apps.sitemaps.views import SitemapView

from marchena.sitemaps import (
    AuthorSitemap,
    BlogSitemap,
    CategorySitemap,
    PostSitemap,
    TagSitemap,
)

class AuthorSitemapView(SitemapView):
    sitemap = AuthorSitemap


class BlogSitemapView(SitemapView):
    sitemap = BlogSitemap


class CategorySitemapView(SitemapView):
    sitemap = CategorySitemap


class NewsSitemapView(SitemapView):

    sitemap = PostSitemap
    template_name = 'yepes/sitemap_news.xml'

    def get_sitemap(self, **kwargs):
        kwargs.setdefault('published_from',
                          timezone.now() - timedelta(days=2))
        return super(NewsSitemapView, self).get_sitemap(**kwargs)


class PostSitemapView(SitemapView):
    sitemap = PostSitemap


class TagSitemapView(SitemapView):
    sitemap = TagSitemap

