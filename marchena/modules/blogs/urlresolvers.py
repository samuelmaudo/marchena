# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from yepes.apps import apps
from yepes.urlresolvers import full_reverse

Blog = apps.get_model('blogs', 'Blog')


class BlogUrlGenerator(object):

    url_name = None

    def __init__(self, url_name=None):
        if url_name is not None:
            self.url_name = url_name

    def __iter__(self):
        if not self.url_name:
            msg = ('Provide an url_name.')
            raise ImproperlyConfigured(msg)

        return (
            full_reverse(self.url_name,
                         kwargs={'blog_slug': blog.slug})
            for blog
            in Blog.cache.all()
        )

