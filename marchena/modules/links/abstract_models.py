# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.model_mixins import (
    Illustrated,
    Logged,
    Slugged,
)
from yepes.utils import slugify


@python_2_unicode_compatible
class AbstractLink(Illustrated, Logged):

    blog = fields.CachedForeignKey(
            'blogs.Blog',
            related_name='links',
            verbose_name=_('Blog'))
    name = fields.CharField(
            max_length=63,
            verbose_name=_('Name'),
            help_text=_('Example: A framework for perfectionists'))
    url = models.URLField(
            max_length=127,
            verbose_name=_('Web Address'),
            help_text=_("Example: <code>http://www.djangoproject.com/</code> &mdash; don't forget the <code>http://</code>"))
    rss = models.URLField(
            blank=True,
            max_length=127,
            verbose_name=_('RSS Address'),
            help_text=_("Example: <code>http://www.djangoproject.com/rss.xml</code> &mdash; don't forget the <code>http://</code>"))
    description = models.CharField(
            max_length=255,
            blank=True,
            verbose_name=_('Description'),
            help_text=_('This will be shown when someone hovers the link in the blogroll, or optionally below the link.'))

    category = models.ForeignKey(
            'LinkCategory',
            null=True,
            related_name='links',
            verbose_name=_('Category'))

    class Meta:
        abstract = True
        folder_name = 'blog_links'
        ordering = ['name']
        verbose_name = _('Link')
        verbose_name_plural = _('Links')

    def __str__(self):
        return self.name

    def get_upload_path(self, filename):
        filename = slugify(self.name, ascii=True).replace('-', '_')
        return super(AbstractLink, self).get_upload_path(filename)


@python_2_unicode_compatible
class AbstractLinkCategory(Slugged):

    blog = fields.CachedForeignKey(
            'blogs.Blog',
            related_name='link_categories',
            verbose_name=_('Blog'))
    name = fields.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Name'))
    description = models.TextField(
            blank=True,
            verbose_name=_('Description'),
            help_text=_('The description is usually not prominent.'))

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Link Category')
        verbose_name_plural = _('Link Categories')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {
            #'blog_pk': self.blog.pk,
            'blog_slug': self.blog.slug,
            #'link_category_pk': self.pk,
            'link_category_slug': self.slug,
        }
        return reverse('link_list', kwargs=kwargs)

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )

