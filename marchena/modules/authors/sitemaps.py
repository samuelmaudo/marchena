# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.contrib.sitemaps import FullUrlSitemap

Author = apps.get_model('authors', 'Author')


class AuthorSitemap(FullUrlSitemap):

    changefreq = 'weekly'
    priority = 0.3

    def get_queryset(self):
        qs = Author.objects.get_queryset()
        qs = qs.filter(is_active=True)
        return qs.order_by('-pk')

    def items(self):
        qs = self.get_queryset()
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()

