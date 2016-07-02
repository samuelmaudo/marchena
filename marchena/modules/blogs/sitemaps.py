# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.contrib.sitemaps import FullUrlSitemap

Blog = apps.get_model('blogs', 'Blog')


class BlogSitemap(FullUrlSitemap):

    changefreq = 'daily'
    priority = 0.7

    def items(self):
        qs = Blog.objects.order_by('-pk')
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()

