# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.translation import ugettext as _


def forwards(apps, schema_editor):

    Blog = apps.get_model('blogs', 'Blog')
    blog = Blog.objects.get(pk=1)

    Category = apps.get_model('posts', 'Category')
    category = Category(**{
        'pk': 1,
        'blog': blog,
        'name': _('Uncategorized'),
        'slug': _('Uncategorized'),
    })
    category.save(force_insert=True)

    Post = apps.get_model('posts', 'Post')
    post = Post(**{
        'pk': 1,
        'blog': blog,
        'title': _('Hello world!'),
        'slug': _('Hello world!'),
        'content': _('Welcome to Marchena. This is your first post. '
                     'Edit or delete it, then start blogging!'),
    })
    post.save(force_insert=True)
    post.categories.add(category)


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0002_initial_data'),
        ('posts', '0001_initial_schema'),
    ]

    initial = True

    operations = [
        migrations.RunPython(forwards),
    ]
