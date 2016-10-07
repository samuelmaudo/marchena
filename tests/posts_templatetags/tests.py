# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import SimpleTestCase

from yepes.test_mixins import TemplateTagsMixin

from marchena.modules.posts.templatetags.posts import (
    CalendarTag,
    GetArchivesTag,
    GetCategoryTag,
    GetCategoriesTag,
    GetNextPostTag,
    GetPopularPostsTag,
    GetPostTag,
    GetPostsTag,
    GetPreviousPostTag,
    GetRecentPostsTag,
    GetRelatedPostsTag,
    GetTagTag,
    GetTagsTag,
    LastModificationTag,
    LastPublicationTag,
    NextPostLinkTag,
    PostAuthorsTag,
    PostCategoriesTag,
    PostTagsTag,
    PreviousPostLinkTag,
    TagCloudTag,
)


class PostsTagsTest(TemplateTagsMixin, SimpleTestCase):

    requiredLibraries = ['posts']

    def test_calendar_syntax(self):
        self.checkSyntax(
            CalendarTag,
            '{% calendar[ year[ month[ user]]] %}',
        )

    def test_get_archives_syntax(self):
        self.checkSyntax(
            GetArchivesTag,
            '{% get_archives[ period[ user[ ordering]]][ as variable_name] %}',
        )

    def test_get_category_syntax(self):
        self.checkSyntax(
            GetCategoryTag,
            '{% get_category category_slug[ blog][ as variable_name] %}',
        )

    def test_get_categories_syntax(self):
        self.checkSyntax(
            GetCategoriesTag,
            '{% get_categories *category_slugs[ blog][ as variable_name] %}',
        )

    def test_get_next_post_syntax(self):
        self.checkSyntax(
            GetNextPostTag,
            '{% get_next_post[ post[ user[ in_same_blog]]][ as variable_name] %}',
        )

    def test_get_popular_posts_syntax(self):
        self.checkSyntax(
            GetPopularPostsTag,
            '{% get_popular_posts[ limit[ user[ author[ blog[ category[ tag[ days]]]]]]][ as variable_name] %}',
        )

    def test_get_post_syntax(self):
        self.checkSyntax(
            GetPostTag,
            '{% get_post post_id[ as variable_name] %}',
        )

    def test_get_posts_syntax(self):
        self.checkSyntax(
            GetPostsTag,
            '{% get_posts[ limit[ user[ ordering[ author[ blog[ category[ tag[ days]]]]]]]][ as variable_name] %}',
        )

    def test_get_previous_post_syntax(self):
        self.checkSyntax(
            GetPreviousPostTag,
            '{% get_previous_post[ post[ user[ in_same_blog]]][ as variable_name] %}',
        )

    def test_get_recent_posts_syntax(self):
        self.checkSyntax(
            GetRecentPostsTag,
            '{% get_recent_posts[ limit[ user[ author[ blog[ category[ tag]]]]]][ as variable_name] %}',
        )

    def test_get_related_posts_syntax(self):
        self.checkSyntax(
            GetRelatedPostsTag,
            '{% get_related_posts[ post[ limit[ in_same_blog]]][ as variable_name] %}',
        )

    def test_get_tag_syntax(self):
        self.checkSyntax(
            GetTagTag,
            '{% get_tag tag_slug[ as variable_name] %}',
        )

    def test_get_tags_syntax(self):
        self.checkSyntax(
            GetTagsTag,
            '{% get_tags *tag_slugs[ as variable_name] %}',
        )

    def test_last_modification_syntax(self):
        self.checkSyntax(
            LastModificationTag,
            '{% last_modification[ format[ user]] %}',
        )

    def test_last_publication_syntax(self):
        self.checkSyntax(
            LastPublicationTag,
            '{% last_publication[ format[ user]] %}',
        )

    def test_next_post_link_syntax(self):
        self.checkSyntax(
            NextPostLinkTag,
            '{% next_post_link[ format[ link[ post[ user[ in_same_blog]]]]] %}',
        )

    def test_post_authors_syntax(self):
        self.checkSyntax(
            PostAuthorsTag,
            '{% post_authors[ separator[ last_separator[ post]]][ as variable_name] %}',
        )

    def test_post_categories_syntax(self):
        self.checkSyntax(
            PostCategoriesTag,
            '{% post_categories[ separator[ last_separator[ post]]][ as variable_name] %}',
        )

    def test_post_tags_syntax(self):
        self.checkSyntax(
            PostTagsTag,
            '{% post_tags[ separator[ last_separator[ post]]][ as variable_name] %}',
        )

    def test_previous_post_link_syntax(self):
        self.checkSyntax(
            PreviousPostLinkTag,
            '{% previous_post_link[ format[ link[ post[ user[ in_same_blog]]]]] %}',
        )

    def test_tag_cloud_syntax(self):
        self.checkSyntax(
            TagCloudTag,
            '{% tag_cloud[ limit] %}',
        )

