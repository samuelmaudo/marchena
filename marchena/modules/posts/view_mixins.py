# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils import six
from django.utils.translation import ugettext as _

from yepes.loading import get_model
from yepes.types import Undefined

Category = get_model('posts', 'Category')
CategoryManager = Category._default_manager
Tag = get_model('posts', 'Tag')
TagManager = Tag._default_manager


class CategoryMixin(object):

    _category = Undefined
    category = None
    category_field = 'category'
    require_category = False

    def get_category(self):
        if self._category is Undefined:

            category = None
            category_pk = None
            category_slug = None
            if self.category:
                if isinstance(self.category, six.integer_types):
                    category_pk = self.category
                elif isinstance(self.category, six.string_types):
                    category_slug = self.category
            else:
                category_pk = self.kwargs.get('category_pk')
                category_slug = self.kwargs.get('category_slug')
                if (not category_pk
                        and not category_slug
                        and (self, 'allow_get_parameters', False)):
                    category_slug = (self.request.GET.get('category')
                                     or self.request.GET.get('c'))

            try:
                if category_pk:
                    category = CategoryManager.get(pk=category_pk)
                elif category_slug:
                    category = CategoryManager.get(slug=category_slug)
            except Category.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': Category._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if category is None and self.require_category:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': Category._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._category = category

        return self._category

    def get_context_data(self, **kwargs):
        context = super(CategoryMixin, self).get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context

    def get_queryset(self):
        qs = super(CategoryMixin, self).get_queryset()
        if self.get_category():
            qs = qs.filter(**{self.category_field: self.get_category()})
        return qs


class TagMixin(object):

    _tag = Undefined
    tag = None
    tag_field = 'tag'
    require_tag = False

    def get_tag(self):
        if self._tag is Undefined:

            tag = None
            tag_pk = None
            tag_slug = None
            if self.tag:
                if isinstance(self.tag, six.integer_types):
                    tag_pk = self.tag
                elif isinstance(self.tag, six.string_types):
                    tag_slug = self.tag
            else:
                tag_pk = self.kwargs.get('tag_pk')
                tag_slug = self.kwargs.get('tag_slug')
                if (not tag_pk
                        and not tag_slug
                        and (self, 'allow_get_parameters', False)):
                    tag_slug = (self.request.GET.get('tag')
                                or self.request.GET.get('t'))

            try:
                if tag_pk:
                    tag = TagManager.get(pk=tag_pk)
                elif tag_slug:
                    tag = TagManager.get(slug=tag_slug)
            except Tag.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': Tag._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if tag is None and self.require_tag:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': Tag._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._tag = tag

        return self._tag

    def get_context_data(self, **kwargs):
        context = super(TagMixin, self).get_context_data(**kwargs)
        context['tag'] = self.get_tag()
        return context

    def get_queryset(self):
        qs = super(TagMixin, self).get_queryset()
        if self.get_tag():
            qs = qs.filter(**{self.tag_field: self.get_tag()})
        return qs

