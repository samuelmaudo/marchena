# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six
from django.utils import translation

from yepes.apps import apps
from yepes.contrib.sitemaps import FullUrlSitemap

Category = apps.get_model('posts', 'Category')
Post = apps.get_model('posts', 'Post')
Tag = apps.get_model('posts', 'Tag')


class CategorySitemap(FullUrlSitemap):

    changefreq = 'daily'
    priority = 0.6

    def __init__(self, blog_pk=None, blog_slug=None):
        self.blog_pk = blog_pk
        self.blog_slug = blog_slug

    def get_queryset(self):
        qs = Category.objects.get_queryset()
        qs = qs.defer('description')
        return qs.order_by('-pk')

    def items(self):
        qs = self.get_queryset()
        if self.blog_pk is not None:
            qs = qs.filter(blog_id=self.blog_pk)
        elif self.blog_slug is not None:
            qs = qs.filter(blog__slug=self.blog_slug)
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()


class NewsSitemap(FullUrlSitemap):

    def __init__(self, blog_pk=None, blog_slug=None, published_from=None):
        self.blog_pk = blog_pk
        self.blog_slug = blog_slug
        self.published_from = published_from

    def get_queryset(self):
        qs = Post.objects.get_queryset()
        qs = qs.published()
        qs = qs.defer('excerpt', 'excerpt_html')
        qs = qs.defer('content', 'content_html')
        return qs.order_by('-publish_from')

    def get_urls(self, page=1, *args, **kwargs):
        if self.paginate:
            items = self.paginator.page(page).object_list
        elif page == 1:
            items = self.items()
        else:
            items = ()

        urls = [
            {
                'item': i,
                'location': self._Sitemap__get('location', i),
                'lastmod': self._Sitemap__get('lastmod', i, None),
                'changefreq': self._Sitemap__get('changefreq', i, ''),
                'priority': six.text_type(self._Sitemap__get('priority', i, '')),
                'publication_name': self._Sitemap__get('publication_name', i),
                'publication_language': self._Sitemap__get('publication_language', i),
                'access': self._Sitemap__get('access', i, ''),
                'genres': self._Sitemap__get('genres', i, ()),
                'date': self._Sitemap__get('date', i),
                'title': self._Sitemap__get('title', i),
                'keywords': self._Sitemap__get('keywords', i, ()),
            }
            for i
            in items
        ]
        return urls

    def items(self):
        qs = self.get_queryset()
        if self.blog_pk is not None:
            qs = qs.filter(blog_id=self.blog_pk)
        elif self.blog_slug is not None:
            qs = qs.filter(blog__slug=self.blog_slug)
        if self.published_from is not None:
            qs = qs.filter(publish_from__gt=self.published_from)
        if self.limit:
            qs = qs[:self.limit]
        return qs.prefetch_related('tags')

    def date(self, obj):
        return obj.publish_from

    def genres(self, obj):
        return ('PressRelease', 'Blog')

    def keywords(self, obj):
        return obj.tags.values_list('name', flat=True)

    def lastmod(self, obj):
        return obj.last_modified

    def publication_language(self, obj):
        return translation.get_language()[:2]

    def publication_name(self, obj):
        return obj.blog.title

    def title(self, obj):
        return obj.title


class PostSitemap(FullUrlSitemap):

    changefreq = 'weekly'
    priority = 0.4

    def __init__(self, blog_pk=None, blog_slug=None):
        self.blog_pk = blog_pk
        self.blog_slug = blog_slug

    def get_queryset(self):
        qs = Post.objects.get_queryset()
        qs = qs.published()
        qs = qs.defer('excerpt', 'excerpt_html')
        qs = qs.defer('content', 'content_html')
        return qs.order_by('-publish_from')

    def items(self):
        qs = self.get_queryset()
        if self.blog_pk is not None:
            qs = qs.filter(blog_id=self.blog_pk)
        elif self.blog_slug is not None:
            qs = qs.filter(blog__slug=self.blog_slug)
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()

    def lastmod(self, obj):
        return obj.last_modified


class TagSitemap(FullUrlSitemap):

    changefreq = 'monthly'
    priority = 0.2

    def get_queryset(self):
        qs = Tag.objects.get_queryset()
        qs = qs.defer('description')
        return qs.order_by('-pk')

    def items(self):
        qs = self.get_queryset()
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()

