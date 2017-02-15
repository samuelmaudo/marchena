# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0003_initial_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Modified'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user_agent',
            field=yepes.fields.TextField(blank=True, verbose_name='User Agent'),
        ),
    ]
