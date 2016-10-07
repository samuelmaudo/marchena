# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six
from django.utils.itercompat import is_iterable
from django.views.generic import (
    ArchiveIndexView,
    DayArchiveView,
    MonthArchiveView,
    YearArchiveView,
)

from yepes.apps import apps
from yepes.view_mixins import CacheMixin

BlogMixin = apps.get_class('blogs.view_mixins', 'BlogMixin')

Post = apps.get_model('posts', 'Post')


class PostArchiveIndexView(BlogMixin, CacheMixin, ArchiveIndexView):

    context_object_name = 'post_list'
    date_field = 'publish_from'
    date_list_period = 'month'
    model = Post
    require_blog = False

    def get_queryset(self):
        qs = super(PostArchiveIndexView, self).get_queryset()
        qs = qs.published(self.request.user)
        return qs

    def get_template_names(self):
        templates = []
        if isinstance(self.template_name, six.string_types):
            templates.append(self.template_name)
        elif is_iterable(self.template_name):
            templates.extend(self.template_name)

        templates.append('posts/archive_index.html')
        return templates


class PostArchiveYearView(BlogMixin, CacheMixin, YearArchiveView):

    allow_empty = True
    context_object_name = 'post_list'
    date_field = 'publish_from'
    model = Post
    require_blog = False
    year_format = '%Y'

    def get_queryset(self):
        qs = super(PostArchiveYearView, self).get_queryset()
        qs = qs.published(self.request.user)
        return qs

    def get_template_names(self):
        templates = []
        if isinstance(self.template_name, six.string_types):
            templates.append(self.template_name)
        elif is_iterable(self.template_name):
            templates.extend(self.template_name)

        templates.append('posts/archive_year.html')
        return templates


class PostArchiveMonthView(BlogMixin, CacheMixin, MonthArchiveView):

    allow_empty = True
    context_object_name = 'post_list'
    date_field = 'publish_from'
    model = Post
    month_format = '%m'
    require_blog = False
    year_format = '%Y'

    def get_queryset(self):
        qs = super(PostArchiveMonthView, self).get_queryset()
        qs = qs.published(self.request.user)
        return qs

    def get_template_names(self):
        templates = []
        if isinstance(self.template_name, six.string_types):
            templates.append(self.template_name)
        elif is_iterable(self.template_name):
            templates.extend(self.template_name)

        templates.append('posts/archive_month.html')
        return templates


class PostArchiveDayView(BlogMixin, CacheMixin, DayArchiveView):

    allow_empty = True
    context_object_name = 'post_list'
    date_field = 'publish_from'
    day_format = '%d'
    model = Post
    month_format = '%m'
    require_blog = False
    year_format = '%Y'

    def get_queryset(self):
        qs = super(PostArchiveDayView, self).get_queryset()
        qs = qs.published(self.request.user)
        return qs

    def get_template_names(self):
        templates = []
        if isinstance(self.template_name, six.string_types):
            templates.append(self.template_name)
        elif is_iterable(self.template_name):
            templates.extend(self.template_name)

        templates.append('posts/archive_day.html')
        return templates

