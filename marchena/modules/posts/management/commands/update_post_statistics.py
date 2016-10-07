# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from yepes.loading import LazyModel

Post = LazyModel('posts', 'Post')
PostRecord = LazyModel('posts', 'PostRecord')


class Command(BaseCommand):
    help = 'Collects the statistics of the posts and calculates their score.'
    requires_system_checks = True

    def handle(self, **options):
        PostRecord.objects.calculate_stats()
        PostRecord.objects.calculate_score()
        Post.objects.update_stats()
        verbosity = int(options.get('verbosity', '1'))
        if verbosity > 0:
            self.stdout.write('Stats were successfully updated.')

