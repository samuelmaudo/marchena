# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.translation import ugettext as _


def forwards(apps, schema_editor):

    Blog = apps.get_model('blogs', 'Blog')
    blog = Blog(**{
        'pk': 1,
        'title': _('My blog'),
        'slug': _('My blog'),
    })
    blog.save(force_insert=True)


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0001_initial_schema'),
    ]

    initial = True

    operations = [
        migrations.RunPython(forwards),
    ]
