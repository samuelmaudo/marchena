# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import yepes.model_mixins.illustrated
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0001_initial_schema'),
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='LinkCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', yepes.fields.SlugField(help_text='URL friendly version of the main title. It is usually all lowercase and contains only letters, numbers and hyphens.', unique=True, verbose_name='Slug')),
                ('blog', yepes.fields.CachedForeignKey(related_name='link_categories', verbose_name='Blog', to='blogs.Blog')),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('description', yepes.fields.TextField(help_text='The description is usually not prominent.', verbose_name='Description', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Link Category',
                'verbose_name_plural': 'Link Categories',
            },
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', yepes.fields.ImageField(upload_to=yepes.model_mixins.illustrated.image_upload_to, width_field='image_width', height_field='image_height', max_length=127, blank=True, verbose_name='Image')),
                ('image_height', yepes.fields.IntegerField(verbose_name='Image Height', min_value=0, null=True, editable=False, blank=True)),
                ('image_width', yepes.fields.IntegerField(verbose_name='Image Width', min_value=0, null=True, editable=False, blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('blog', yepes.fields.CachedForeignKey(related_name='links', verbose_name='Blog', to='blogs.Blog')),
                ('name', yepes.fields.CharField(help_text='Example: A framework for perfectionists', max_length=63, verbose_name='Name')),
                ('url', models.URLField(help_text="Example: <code>http://www.djangoproject.com/</code> &mdash; don't forget the <code>http://</code>", max_length=127, verbose_name='Web Address')),
                ('rss', models.URLField(help_text="Example: <code>http://www.djangoproject.com/rss.xml</code> &mdash; don't forget the <code>http://</code>", max_length=127, verbose_name='RSS Address', blank=True)),
                ('description', yepes.fields.CharField(help_text='This will be shown when someone hovers the link in the blogroll, or optionally below the link.', max_length=255, verbose_name='Description', blank=True)),
                ('category', yepes.fields.CachedForeignKey(related_name='links', verbose_name='Category', to='links.LinkCategory', null=True, blank=True)),
            ],
            options={
                'folder_name': 'blog_links',
                'ordering': ['name'],
                'verbose_name': 'Link',
                'verbose_name_plural': 'Links',
            },
        ),
    ]
