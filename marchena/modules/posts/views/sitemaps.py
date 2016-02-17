# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from django.utils import timezone

from yepes.contrib.sitemaps.views import SitemapView
from yepes.loading import get_class

CategorySitemap = get_class('posts.sitemaps', 'CategorySitemap')
NewsSitemap = get_class('posts.sitemaps', 'NewsSitemap')
PostSitemap = get_class('posts.sitemaps', 'PostSitemap')
TagSitemap = get_class('posts.sitemaps', 'TagSitemap')


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

