# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import marchena.modules.authors.managers


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Author',
                'verbose_name_plural': 'Authors',
            },
            bases=(
                'auth.user',
            ),
            managers=[
                ('objects', marchena.modules.authors.managers.AuthorManager()),
            ],
        ),
    ]
