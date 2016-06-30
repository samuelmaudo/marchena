# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.sitemaps import FullUrlSitemap
from yepes.loading import get_model

Blog = get_model('blogs', 'Blog')


class BlogSitemap(FullUrlSitemap):

    changefreq = 'daily'
    priority = 0.7

    def items(self):
        qs = Blog.objects.order_by('-pk')
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()

