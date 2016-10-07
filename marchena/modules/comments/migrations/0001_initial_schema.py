# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields
import django.db.models.deletion
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial_schema'),
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='CommentStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', yepes.fields.IntegerField(default=0, min_value=0, db_index=True, verbose_name='Index', blank=True)),
                ('label', yepes.fields.CharField(max_length=63, verbose_name='Label')),
                ('api_id', yepes.fields.IdentifierField(help_text='This field is for internally identify the comment status. Can only contain lowercase letters, numbers and underscores.', verbose_name='API id')),
                ('color', yepes.fields.ColorField(help_text='This color is used on the admin site for visually identify the comment status.', verbose_name='Color')),
                ('publish_comment', yepes.fields.BooleanField(default=True, help_text='Uncheck this box to make the comments effectively disappear from the blog.', verbose_name='Publishes Comments')),
                ('comment_replacement', yepes.fields.TextField(help_text='The content of this field will replace the text of the user comments. E.g.: "Inappropriate comment."', verbose_name='Comment Replacement', blank=True)),
            ],
            options={
                'ordering': ['label'],
                'verbose_name': 'Comment Status',
                'verbose_name_plural': 'Comment Statuses',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent', blank=True, to='comments.Comment', null=True)),
                ('author_name', yepes.fields.CharField(max_length=63, verbose_name='Name', blank=True)),
                ('author_email', yepes.fields.EmailField(verbose_name='Email Address', blank=True)),
                ('author_url', models.URLField(max_length=127, verbose_name='URL', blank=True)),
                ('ip_address', models.GenericIPAddressField(unpack_ipv4=True, null=True, verbose_name='IP Address', blank=True)),
                ('user_agent', yepes.fields.CharField(max_length=255, verbose_name='User Agent', blank=True)),
                ('karma', yepes.fields.IntegerField(default=0, verbose_name='Karma', blank=True)),
                ('status', yepes.fields.CachedForeignKey(related_name='comments', on_delete=django.db.models.deletion.PROTECT, verbose_name='Status', to='comments.CommentStatus')),
                ('is_published', yepes.fields.BooleanField(default=True, verbose_name='Is Published?', editable=False)),
            ],
            options={
                'ordering': ['-creation_date'],
                'permissions': [('can_moderate', 'Can moderate comments')],
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
            },
        ),
        migrations.AlterIndexTogether(
            name='comment',
            index_together=set([('status', 'creation_date')]),
        ),
    ]
