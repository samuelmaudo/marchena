# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.contrib.sitemaps import FullUrlSitemap

Blog = apps.get_model('blogs', 'Blog')


class BlogSitemap(FullUrlSitemap):

    changefreq = 'daily'
    priority = 0.8

    def get_queryset(self):
        qs = Blog.objects.get_queryset()
        qs = qs.defer('description', 'description_html')
        return qs.order_by('-pk')

    def items(self):
        qs = self.get_queryset()
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()

