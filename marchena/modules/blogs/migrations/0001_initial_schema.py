
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import yepes.model_mixins.illustrated
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
        ('authors', '0001_initial_schema'),
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meta_title', yepes.fields.CharField(help_text='Optional title to be used in the HTML title tag. If left blank, the main title field will be used.', max_length=127, verbose_name='Title', blank=True)),
                ('meta_description', yepes.fields.TextField(help_text='Optional description to be used in the description meta tag. If left blank, the content field will be used.', verbose_name='Description', blank=True)),
                ('meta_keywords', yepes.fields.CommaSeparatedField(separator=', ', blank=True, help_text='Optional keywords to be used in the keywords meta tag. If left blank, will be extracted from the description.', verbose_name='Keywords')),
                ('slug', yepes.fields.SlugField(help_text='URL friendly version of the main title. It is usually all lowercase and contains only letters, numbers and hyphens.', unique=True, verbose_name='Slug')),
                ('image', yepes.fields.ImageField(upload_to=yepes.model_mixins.illustrated.image_upload_to, width_field='image_width', height_field='image_height', max_length=127, blank=True, verbose_name='Image')),
                ('image_height', yepes.fields.IntegerField(verbose_name='Image Height', min_value=0, null=True, editable=False, blank=True)),
                ('image_width', yepes.fields.IntegerField(verbose_name='Image Width', min_value=0, null=True, editable=False, blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('title', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Title')),
                ('subtitle', yepes.fields.CharField(help_text='In a few words, explain what this site is about.', max_length=255, verbose_name='Subtitle', blank=True)),
                ('description', yepes.fields.RichTextField(help_text='Or, maybe, you want to write a more detailed explanation.', verbose_name='Description', blank=True)),
                ('description_html', yepes.fields.TextField(verbose_name='Description', editable=False, db_column='description_html', blank=True)),
                ('authors', models.ManyToManyField(related_name='blogs', verbose_name='Authors', to='authors.Author')),
            ],
            options={
                'folder_name': 'blog_images',
                'ordering': ['title'],
                'verbose_name': 'Blog',
                'verbose_name_plural': 'Blogs',
            },
        ),
    ]
