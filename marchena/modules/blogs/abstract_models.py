# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.cache import LookupTable
from yepes.model_mixins import (
    Illustrated,
    Logged,
    MetaData,
    Slugged,
)
from yepes.urlresolvers import full_reverse


@python_2_unicode_compatible
class AbstractBlog(Illustrated, Slugged, MetaData, Logged):

    title = fields.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Title'))
    subtitle = fields.CharField(
            blank=True,
            max_length=255,
            verbose_name=_('Subtitle'),
            help_text=_('In a few words, explain what this site is about.'))
    description = fields.RichTextField(
            blank=True,
            verbose_name=_('Description'),
            help_text=_('Or, maybe, you want to write a more detailed explanation.'))

    authors = models.ManyToManyField(
            'authors.Author',
            related_name='blogs',
            verbose_name=_('Authors'))

    objects = models.Manager()
    cache = LookupTable(
            indexed_fields=['slug'],
            prefetch_related=['authors', 'categories'])

    class Meta:
        abstract = True
        folder_name = 'blog_images'
        ordering = ['title']
        verbose_name = _('Blog')
        verbose_name_plural = _('Blogs')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        kwargs = {'blog_slug': self.slug}
        return reverse('post_list', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {'blog_slug': self.slug}
        return full_reverse('post_feed', kwargs=kwargs)

    def get_upload_path(self, filename):
        filename = self.slug.replace('-', '_')
        return super(AbstractBlog, self).get_upload_path(filename)

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('title__icontains', )

