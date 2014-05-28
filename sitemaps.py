# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps.sitemaps import FullUrlSitemap
from yepes.loading import get_model

Author = get_model('marchena', 'Author')
AuthorManager = Author._default_manager
Blog = get_model('marchena', 'Blog')
BlogManager = Blog._default_manager
Category = get_model('marchena', 'Category')
CategoryManager = Category._default_manager
Post = get_model('marchena', 'Post')
PostManager = Post._default_manager
Tag = get_model('marchena', 'Tag')
TagManager = Tag._default_manager


class AuthorSitemap(FullUrlSitemap):

    changefreq = 'weekly'
    priority = 0.3

    def items(self):
        qs = AuthorManager.order_by('-pk')
        qs = qs.filter(is_active=True)
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()


class BlogSitemap(FullUrlSitemap):

    changefreq = 'daily'
    priority = 0.7

    def items(self):
        qs = BlogManager.order_by('-pk')
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()


class CategorySitemap(FullUrlSitemap):

    changefreq = 'weekly'
    priority = 0.3

    def __init__(self, blog_pk=None, blog_slug=None):
        self.blog_pk = blog_pk
        self.blog_slug = blog_slug

    def items(self):
        qs = CategoryManager.order_by('-pk')
        if self.blog_pk is not None:
            qs = qs.filter(blog_id=self.blog_pk)
        elif self.blog_slug is not None:
            qs = qs.filter(blog__slug=self.blog_slug)
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()


class PostSitemap(FullUrlSitemap):

    def __init__(self, blog_pk=None, blog_slug=None, published_from=None):
        self.blog_pk = blog_pk
        self.blog_slug = blog_slug
        self.published_from = published_from

    def items(self):
        qs = PostManager.order_by('-publish_from')
        qs = qs.published()
        if self.blog_pk is not None:
            qs = qs.filter(blog_id=self.blog_pk)
        elif self.blog_slug is not None:
            qs = qs.filter(blog__slug=self.blog_slug)
        if self.published_from is not None:
            qs = qs.filter(publish_from__gt=self.published_from)
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()

    def lastmod(self, obj):
        return obj.last_modified


class TagSitemap(FullUrlSitemap):

    changefreq = 'weekly'
    priority = 0.3

    def items(self):
        qs = TagManager.order_by('-pk')
        if self.limit:
            qs = qs[:self.limit]
        return qs.iterator()

