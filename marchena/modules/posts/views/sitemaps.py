# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from django.utils import timezone

from yepes.apps import apps
from yepes.contrib.sitemaps.views import SitemapView

CategorySitemap = apps.get_class('posts.sitemaps', 'CategorySitemap')
NewsSitemap = apps.get_class('posts.sitemaps', 'NewsSitemap')
PostSitemap = apps.get_class('posts.sitemaps', 'PostSitemap')
TagSitemap = apps.get_class('posts.sitemaps', 'TagSitemap')


class CategorySitemapView(SitemapView):

    sitemap_class = CategorySitemap

    def get_sitemap_kwargs(self):
        kwargs = super(CategorySitemapView, self).get_sitemap_kwargs()
        if 'blog_pk' in self.kwargs:
            kwargs['blog_pk'] = self.kwargs['blog_pk']
        elif 'blog_slug' in self.kwargs:
            kwargs['blog_slug'] = self.kwargs['blog_slug']

        return kwargs


class NewsSitemapView(SitemapView):

    sitemap_class = NewsSitemap
    template_name = 'sitemap_news.xml'

    def get_sitemap_kwargs(self):
        kwargs = super(NewsSitemapView, self).get_sitemap_kwargs()
        if 'blog_pk' in self.kwargs:
            kwargs['blog_pk'] = self.kwargs['blog_pk']
        elif 'blog_slug' in self.kwargs:
            kwargs['blog_slug'] = self.kwargs['blog_slug']

        kwargs['published_from'] = timezone.now() - timedelta(days=2)
        return kwargs


class PostSitemapView(SitemapView):

    sitemap_class = PostSitemap

    def get_sitemap_kwargs(self):
        kwargs = super(PostSitemapView, self).get_sitemap_kwargs()
        if 'blog_pk' in self.kwargs:
            kwargs['blog_pk'] = self.kwargs['blog_pk']
        elif 'blog_slug' in self.kwargs:
            kwargs['blog_slug'] = self.kwargs['blog_slug']

        return kwargs


class TagSitemapView(SitemapView):
    sitemap_class = TagSitemap

