# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from django.utils import timezone

from yepes.contrib.sitemaps.views import SitemapView

from marchena.sitemaps import (
    AuthorSitemap,
    BlogSitemap,
    CategorySitemap,
    NewsSitemap,
    PostSitemap,
    TagSitemap,
)

class AuthorSitemapView(SitemapView):
    sitemap_class = AuthorSitemap


class BlogSitemapView(SitemapView):
    sitemap_class = BlogSitemap


class CategorySitemapView(SitemapView):
    sitemap_class = CategorySitemap


class NewsSitemapView(SitemapView):
    sitemap_class = NewsSitemap
    template_name = 'sitemap_news.xml'

    def get_sitemap_kwargs(self):
        kwargs = super(NewsSitemapView, self).get_sitemap_kwargs()
        kwargs['published_from'] = timezone.now() - timedelta(days=2)
        return kwargs


class PostSitemapView(SitemapView):
    sitemap_class = PostSitemap


class TagSitemapView(SitemapView):
    sitemap_class = TagSitemap

