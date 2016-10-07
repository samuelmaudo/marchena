# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils.six import StringIO

from marchena.modules.posts.models import Post


class UpdateStatsTest(TestCase):

    fixtures = ['marchena_tests']
    maxDiff = None

    def test_command(self):

        post_1 = Post.objects.get(pk=4)
        self.assertEqual(post_1.views_count, 0)
        self.assertEqual(post_1.comment_count, 0)
        self.assertEqual(post_1.ping_count, 0)
        self.assertEqual(post_1.score, 0)

        post_2 = Post.objects.get(pk=10)
        self.assertEqual(post_2.views_count, 0)
        self.assertEqual(post_2.comment_count, 0)
        self.assertEqual(post_2.ping_count, 0)
        self.assertEqual(post_2.score, 0)

        post_3 = Post.objects.get(pk=14)
        self.assertEqual(post_3.views_count, 0)
        self.assertEqual(post_3.comment_count, 0)
        self.assertEqual(post_3.ping_count, 0)
        self.assertEqual(post_3.score, 0)

        output = StringIO()
        call_command('update_post_statistics', stdout=output)
        self.assertIn('Stats were successfully updated.', output.getvalue())

        post_1 = Post.objects.get(pk=4)
        self.assertEqual(post_1.views_count, 0)
        self.assertEqual(post_1.comment_count, 7)
        self.assertEqual(post_1.ping_count, 0)
        self.assertEqual(post_1.score, 35)

        post_2 = Post.objects.get(pk=10)
        self.assertEqual(post_2.views_count, 0)
        self.assertEqual(post_2.comment_count, 0)
        self.assertEqual(post_2.ping_count, 0)
        self.assertEqual(post_2.score, 0)

        post_3 = Post.objects.get(pk=14)
        self.assertEqual(post_3.views_count, 0)
        self.assertEqual(post_3.comment_count, 1)
        self.assertEqual(post_3.ping_count, 0)
        self.assertEqual(post_3.score, 5)

        post_2.increase_views_count()
        post_2.increase_views_count()
        post_2.increase_views_count()

        post_3.increase_views_count()

        output = StringIO()
        call_command('update_post_statistics', stdout=output)
        self.assertIn('Stats were successfully updated.', output.getvalue())

        post_1 = Post.objects.get(pk=4)
        self.assertEqual(post_1.views_count, 0)
        self.assertEqual(post_1.comment_count, 7)
        self.assertEqual(post_1.ping_count, 0)
        self.assertEqual(post_1.score, 35)

        post_2 = Post.objects.get(pk=10)
        self.assertEqual(post_2.views_count, 3)
        self.assertEqual(post_2.comment_count, 0)
        self.assertEqual(post_2.ping_count, 0)
        self.assertEqual(post_2.score, 3)

        post_3 = Post.objects.get(pk=14)
        self.assertEqual(post_3.views_count, 1)
        self.assertEqual(post_3.comment_count, 1)
        self.assertEqual(post_3.ping_count, 0)
        self.assertEqual(post_3.score, 6)

