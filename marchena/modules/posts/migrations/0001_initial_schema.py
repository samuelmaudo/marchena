# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import marchena.modules.attachments.processors
import yepes.model_mixins.illustrated
import django.utils.timezone
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
        ('authors', '0001_initial_schema'),
        ('blogs', '0001_initial_schema'),
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meta_title', yepes.fields.CharField(help_text='Optional title to be used in the HTML title tag. If left blank, the main title field will be used.', max_length=127, verbose_name='Title', blank=True)),
                ('meta_description', yepes.fields.TextField(help_text='Optional description to be used in the description meta tag. If left blank, the content field will be used.', verbose_name='Description', blank=True)),
                ('meta_keywords', yepes.fields.CommaSeparatedField(separator=', ', blank=True, help_text='Optional keywords to be used in the keywords meta tag. If left blank, will be extracted from the description.', verbose_name='Keywords')),
                ('slug', yepes.fields.SlugField(help_text='URL friendly version of the main title. It is usually all lowercase and contains only letters, numbers and hyphens.', unique=True, verbose_name='Slug')),
                ('image', yepes.fields.ImageField(upload_to=yepes.model_mixins.illustrated.image_upload_to, width_field='image_width', height_field='image_height', max_length=127, blank=True, verbose_name='Image')),
                ('image_height', yepes.fields.IntegerField(verbose_name='Image Height', min_value=0, null=True, editable=False, blank=True)),
                ('image_width', yepes.fields.IntegerField(verbose_name='Image Width', min_value=0, null=True, editable=False, blank=True)),
                ('blog', yepes.fields.CachedForeignKey(related_name='categories', verbose_name='Blog', to='blogs.Blog')),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('description', yepes.fields.TextField(help_text='The description is usually not prominent.', verbose_name='Description', blank=True)),
            ],
            options={
                'folder_name': 'blog_categories',
                'ordering': ['name'],
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', yepes.fields.SlugField(help_text='URL friendly version of the main title. It is usually all lowercase and contains only letters, numbers and hyphens.', unique=True, verbose_name='Slug')),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('description', yepes.fields.TextField(help_text='The description is usually not prominent.', verbose_name='Description', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meta_title', yepes.fields.CharField(help_text='Optional title to be used in the HTML title tag. If left blank, the main title field will be used.', max_length=127, verbose_name='Title', blank=True)),
                ('meta_description', yepes.fields.TextField(help_text='Optional description to be used in the description meta tag. If left blank, the content field will be used.', verbose_name='Description', blank=True)),
                ('meta_keywords', yepes.fields.CommaSeparatedField(separator=', ', blank=True, help_text='Optional keywords to be used in the keywords meta tag. If left blank, will be extracted from the description.', verbose_name='Keywords')),
                ('slug', yepes.fields.SlugField(help_text='URL friendly version of the main title. It is usually all lowercase and contains only letters, numbers and hyphens.', unique=True, verbose_name='Slug')),
                ('publish_status', models.SmallIntegerField(default=2, db_index=True, verbose_name='Status', choices=[(1, 'Draft'), (2, 'Published'), (3, 'Hidden')])),
                ('publish_from', models.DateTimeField(default=django.utils.timezone.now, help_text="Won't be shown until this time.", null=True, verbose_name='Publish From', blank=True)),
                ('publish_to', models.DateTimeField(help_text="Won't be shown after this time.", null=True, verbose_name='To', blank=True)),
                ('image', yepes.fields.ImageField(upload_to=yepes.model_mixins.illustrated.image_upload_to, width_field='image_width', height_field='image_height', max_length=127, blank=True, verbose_name='Image')),
                ('image_height', yepes.fields.IntegerField(verbose_name='Image Height', min_value=0, null=True, editable=False, blank=True)),
                ('image_width', yepes.fields.IntegerField(verbose_name='Image Width', min_value=0, null=True, editable=False, blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('blog', yepes.fields.CachedForeignKey(related_name='posts', verbose_name='Blog', to='blogs.Blog')),
                ('guid', yepes.fields.GuidField(charset='0123456789abcdef', editable=False, verbose_name='Global Unique Identifier')),
                ('title', yepes.fields.CharField(max_length=255, verbose_name='Title')),
                ('subtitle', yepes.fields.CharField(help_text='Subtitles are optional complements of your title.', max_length=255, verbose_name='Subtitle', blank=True)),
                ('excerpt', yepes.fields.RichTextField(help_text='Excerpts are optional hand-crafted summaries of your content.', verbose_name='Excerpt', blank=True)),
                ('excerpt_html', yepes.fields.TextField(verbose_name='Excerpt', editable=False, db_column='excerpt_html', blank=True)),
                ('content', yepes.fields.RichTextField(verbose_name='Content', processors=[marchena.modules.attachments.processors.attachment_tags], blank=True)),
                ('content_html', yepes.fields.TextField(verbose_name='Content', editable=False, db_column='content_html', blank=True)),
                ('authors', models.ManyToManyField(related_name='posts', verbose_name='Authors', to='authors.Author')),
                ('categories', models.ManyToManyField(related_name='posts', verbose_name='Categories', to='posts.Category', blank=True)),
                ('tags', models.ManyToManyField(related_name='posts', verbose_name='Tags', to='posts.Tag', blank=True)),
                ('comment_status', yepes.fields.BooleanField(default=True, verbose_name='Allow comments on this post')),
                ('ping_status', yepes.fields.BooleanField(default=True, verbose_name='Allow trackbacks and pingbacks to this post')),
                ('views_count', models.PositiveIntegerField(default=0, verbose_name='Views', db_index=True, editable=False, blank=True)),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='Comments', db_index=True, editable=False, blank=True)),
                ('ping_count', models.PositiveIntegerField(default=0, verbose_name='Pings', editable=False, blank=True)),
                ('score', models.PositiveIntegerField(default=0, verbose_name='Score', db_index=True, editable=False, blank=True)),
            ],
            options={
                'folder_name': 'blog_posts',
                'ordering': ['-publish_from'],
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
            },
        ),
        migrations.CreateModel(
            name='PostRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post', models.OneToOneField(related_name='stats', verbose_name='Post', to='posts.Post')),
                ('views_count', models.PositiveIntegerField(default=0, verbose_name='Views', editable=False, blank=True)),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='Comments', editable=False, blank=True)),
                ('ping_count', models.PositiveIntegerField(default=0, verbose_name='Pings', editable=False, blank=True)),
                ('score', models.PositiveIntegerField(default=0, verbose_name='Score', editable=False, blank=True)),
            ],
            options={
                'ordering': ['-score'],
                'verbose_name': 'Post Record',
                'verbose_name_plural': 'Post Records',
            },
        ),
        migrations.AlterIndexTogether(
            name='post',
            index_together=set([('publish_status', 'creation_date')]),
        ),
    ]
