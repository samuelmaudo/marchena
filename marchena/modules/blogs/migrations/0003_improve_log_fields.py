# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0002_initial_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation Date'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='blog',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Modified'),
        ),
    ]
