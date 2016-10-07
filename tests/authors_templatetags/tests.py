# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import SimpleTestCase

from yepes.test_mixins import TemplateTagsMixin

from marchena.modules.authors.templatetags.authors import (
    GetAuthorTag,
    GetAuthorsTag,
)


class AuthorsTagsTest(TemplateTagsMixin, SimpleTestCase):

    requiredLibraries = ['authors']

    def test_get_author_syntax(self):
        self.checkSyntax(
            GetAuthorTag,
            '{% get_author username **options[ as variable_name] %}',
        )

    def test_get_authors_syntax(self):
        self.checkSyntax(
            GetAuthorsTag,
            '{% get_authors *usernames **options[ as variable_name] %}',
        )

