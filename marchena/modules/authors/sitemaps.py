# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.contrib.sitemaps import FullUrlSitemap

Author = apps.get_model('authors', 'Author')


class AuthorSitemap(FullUrlSitemap):

    changefreq = 'weekly'
    priority = 0.3

    def items(self):
        qs = Author.objects.order_by('-pk')
        qs = qs.filter(is_active=True)
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()

