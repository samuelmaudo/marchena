# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial_schema'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    initial = True

    operations = [
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(related_name='comments', verbose_name='Post', to='posts.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(related_name='comments', verbose_name='Author', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='content',
            field=yepes.fields.RichTextField(verbose_name='Comment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='content_html',
            field=yepes.fields.TextField(verbose_name='Comment', editable=False, db_column='content_html', blank=True),
        ),
    ]
