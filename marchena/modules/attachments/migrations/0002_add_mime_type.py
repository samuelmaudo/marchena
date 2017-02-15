# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0001_initial_schema'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='mime_type',
            field=yepes.fields.CharField(blank=True, calculated=True, editable=False, max_length=31, null=True, verbose_name='MIME Type'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Modified'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='size',
            field=yepes.fields.IntegerField(blank=True, calculated=True, editable=False, min_value=0, null=True, verbose_name='Size'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='height',
            field=yepes.fields.IntegerField(blank=True, calculated=True, editable=False, min_value=0, null=True, verbose_name='Height'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='width',
            field=yepes.fields.IntegerField(blank=True, calculated=True, editable=False, min_value=0, null=True, verbose_name='Width'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='attachments', to='attachments.AttachmentCategory', verbose_name='Category'),
        ),
    ]
