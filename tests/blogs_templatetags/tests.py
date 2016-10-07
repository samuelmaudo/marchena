# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import SimpleTestCase

from yepes.test_mixins import TemplateTagsMixin

from marchena.modules.blogs.templatetags.blogs import (
    GetBlogTag,
    GetBlogsTag,
)


class BlogsTagsTest(TemplateTagsMixin, SimpleTestCase):

    requiredLibraries = ['blogs']

    def test_get_blog_syntax(self):
        self.checkSyntax(
            GetBlogTag,
            '{% get_blog blog_slug **options[ as variable_name] %}',
        )

    def test_get_blogs_syntax(self):
        self.checkSyntax(
            GetBlogsTag,
            '{% get_blogs *blog_slugs **options[ as variable_name] %}',
        )

