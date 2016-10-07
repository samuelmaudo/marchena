# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.translation import ugettext as _


def forwards(apps, schema_editor):

    Blog = apps.get_model('blogs', 'Blog')
    blog = Blog.objects.get(pk=1)

    LinkCategory = apps.get_model('links', 'LinkCategory')
    category = LinkCategory(**{
        'pk': 1,
        'blog': blog,
        'name': _('Blogroll'),
        'slug': _('Blogroll'),
    })
    category.save(force_insert=True)

    Link = apps.get_model('links', 'Link')
    link = Link(**{
        'pk': 1,
        'blog': blog,
        'name': _('Django Documentation'),
        'url': 'https://docs.djangoproject.com/',
        'category': category,
    })
    link.save(force_insert=True)


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0002_initial_data'),
        ('links', '0001_initial_schema'),
    ]

    initial = True

    operations = [
        migrations.RunPython(forwards),
    ]
