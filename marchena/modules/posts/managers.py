# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import connections
from django.db.models import F, Q
from django.db.models.manager import Manager

from yepes.conf import settings
from yepes.loading import LazyModel
from yepes.managers import DisplayableManager
from yepes.models import statements
from yepes.utils.aggregates import SumIf

Post = LazyModel('posts', 'Post')
PostRecord = LazyModel('posts', 'PostRecord')

statements.register('update_post_stats', """

    UPDATE "{post}" AS post
       SET post.views_count = record.views_count,
           post.comment_count = record.comment_count,
           post.ping_count = record.ping_count,
           post.score = record.score
      FROM "{record}" AS record
     WHERE record.post_id = post.id;

""", 'postgresql')

statements.register('update_post_stats', """

    UPDATE `{post}` as post, `{record}` as record
       SET post.views_count = record.views_count,
           post.comment_count = record.comment_count,
           post.ping_count = record.ping_count,
           post.score = record.score
     WHERE record.post_id = post.id;

""", 'mysql')

statements.register('update_post_stats', """

    UPDATE "{post}"
       SET (views_count, comment_count, ping_count, score) = (
             SELECT views_count, comment_count, ping_count, score
               FROM "{record}"
              WHERE "{record}".post_id = "{post}".id
           );

""", 'sqlite')

statements.register('update_post_stats', """

    UPDATE "{post}"
       SET views_count = (
             SELECT views_count
               FROM "{record}"
              WHERE "{record}".post_id = "{post}".id
           ),
           comment_count = (
             SELECT comment_count
               FROM "{record}"
              WHERE "{record}".post_id = "{post}".id
           ),
           ping_count = (
             SELECT ping_count
               FROM "{record}"
              WHERE "{record}".post_id = "{post}".id
           ),
           score = (
             SELECT score
               FROM "{record}"
              WHERE "{record}".post_id = "{post}".id
           );

""")


class PostManager(DisplayableManager):

    def update_stats(self):
        conn = connections[self.write_db]
        operation = statements.get_sql(
            'update_post_stats',
            conn.vendor,
        ).format(
            post=Post._meta.db_table,
            record=PostRecord._meta.db_table,
        )
        with conn.cursor() as cursor:
            cursor.execute(operation)


class PostRecordManager(Manager):

    def calculate_comment_count(self):
        posts = Post.objects.annotate(
            current_comment_count=SumIf(1, Q(comments__is_published=True))
        ).values_list(
            'pk', 'current_comment_count',
        )
        for post_id, comment_count in posts:
            record, _ = self.get_or_create(post_id=post_id)
            record.comment_count = comment_count
            record.save(update_fields=['comment_count'])

    def calculate_ping_count(self):
        pass

    def calculate_score(self):
        self.update(
            score=((F('views_count') * settings.POST_VIEW_SCORE)
                   + (F('comment_count') * settings.POST_COMMENT_SCORE))
        )

    def calculate_stats(self):
        self.calculate_views_count()
        self.calculate_comment_count()
        self.calculate_ping_count()

    def calculate_views_count(self):
        pass

