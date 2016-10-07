# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import SimpleTestCase

from yepes.test_mixins import TemplateTagsMixin

from marchena.modules.comments.templatetags.comments import (
    CommentFormTag,
    GetCommentTag,
    GetCommentsTag,
    GetPopularCommentsTag,
    GetPostCommentsTag,
    GetRecentCommentsTag,
    PostCommentsTag,
)


class CommentsTagsTest(TemplateTagsMixin, SimpleTestCase):

    requiredLibraries = ['comments']

    def test_comment_form_syntax(self):
        self.checkSyntax(
            CommentFormTag,
            '{% comment_form[ post[ form]] %}',
        )

    def test_get_comment_syntax(self):
        self.checkSyntax(
            GetCommentTag,
            '{% get_comment comment_id[ as variable_name] %}',
        )

    def test_get_comments_syntax(self):
        self.checkSyntax(
            GetCommentsTag,
            '{% get_comments[ limit[ status[ ordering[ author[ blog[ category[ tag[ days]]]]]]]][ as variable_name] %}',
        )

    def test_get_popular_comments_syntax(self):
        self.checkSyntax(
            GetPopularCommentsTag,
            '{% get_popular_comments[ limit[ status[ author[ blog[ category[ tag[ days]]]]]]][ as variable_name] %}',
        )

    def test_get_post_comments_syntax(self):
        self.checkSyntax(
            GetPostCommentsTag,
            '{% get_post_comments[ limit[ status[ ordering[ post]]]][ as variable_name] %}',
        )

    def test_get_recent_comments_syntax(self):
        self.checkSyntax(
            GetRecentCommentsTag,
            '{% get_recent_comments[ limit[ status[ author[ blog[ category[ tag]]]]]][ as variable_name] %}',
        )

    def test_post_comments_syntax(self):
        self.checkSyntax(
            PostCommentsTag,
            '{% post_comments[ limit[ status[ ordering[ post[ form]]]]] %}',
        )

