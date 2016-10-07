# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import yepes.fields
import marchena.modules.attachments.abstract_models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0001_initial_schema'),
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='AttachmentCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('description', yepes.fields.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Attachment Category',
                'verbose_name_plural': 'Attachment Categories',
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('guid', yepes.fields.GuidField(charset='0123456789abcdef', editable=False, verbose_name='Global Unique Identifier')),
                ('title', yepes.fields.CharField(max_length=63, verbose_name='Title')),
                ('caption', yepes.fields.CharField(max_length=255, verbose_name='Caption', blank=True)),
                ('alt', yepes.fields.CharField(max_length=127, verbose_name='Alternate Text', blank=True)),
                ('description', yepes.fields.TextField(verbose_name='Description', blank=True)),
                ('file', models.FileField(upload_to=marchena.modules.attachments.abstract_models.file_upload_to, max_length=127, blank=True, verbose_name='File')),
                ('external_file', models.URLField(max_length=127, verbose_name='External File', blank=True)),
                ('size', yepes.fields.IntegerField(verbose_name='Size', min_value=0, null=True, editable=False, blank=True)),
                ('height', yepes.fields.IntegerField(verbose_name='Height', min_value=0, null=True, editable=False, blank=True)),
                ('width', yepes.fields.IntegerField(verbose_name='Width', min_value=0, null=True, editable=False, blank=True)),
                ('category', yepes.fields.CachedForeignKey(related_name='attachments', verbose_name='Category', to='attachments.AttachmentCategory', null=True, blank=True)),
            ],
            options={
                'folder_name': 'attachments',
                'ordering': ['title'],
                'verbose_name': 'Attachment',
                'verbose_name_plural': 'Attachments',
            },
        ),
    ]
