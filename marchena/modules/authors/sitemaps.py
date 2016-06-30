# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.sitemaps import FullUrlSitemap
from yepes.loading import get_model

Author = get_model('authors', 'Author')


class AuthorSitemap(FullUrlSitemap):

    changefreq = 'weekly'
    priority = 0.3

    def items(self):
        qs = Author.objects.order_by('-pk')
        qs = qs.filter(is_active=True)
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()

