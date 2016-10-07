# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import SimpleTestCase

from yepes.test_mixins import TemplateTagsMixin

from marchena.modules.links.templatetags.links import (
    GetLinkTag,
    GetLinkCategoryTag,
    GetLinkCategoriesTag,
    GetLinksTag,
)


class LinksTagsTest(TemplateTagsMixin, SimpleTestCase):

    requiredLibraries = ['links']

    def test_get_link_syntax(self):
        self.checkSyntax(
            GetLinkTag,
            '{% get_link link_id **options[ as variable_name] %}',
        )

    def test_get_link_category_syntax(self):
        self.checkSyntax(
            GetLinkCategoryTag,
            '{% get_link_category category_slug **options[ as variable_name] %}',
        )

    def test_get_link_categories_syntax(self):
        self.checkSyntax(
            GetLinkCategoriesTag,
            '{% get_link_categories *category_slugs **options[ as variable_name] %}',
        )

    def test_get_links_syntax(self):
        self.checkSyntax(
            GetLinksTag,
            '{% get_links *link_ids **options[ as variable_name] %}',
        )

