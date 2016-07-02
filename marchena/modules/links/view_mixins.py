# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils import six
from django.utils.translation import ugettext as _

from yepes.apps import apps
from yepes.types import Undefined

LinkCategory = apps.get_model('links', 'LinkCategory')


class LinkCategoryMixin(object):

    _link_category = Undefined
    link_category = None
    link_category_field = 'category'
    require_link_category = False

    def get_link_category(self):
        if self._link_category is Undefined:

            category = None
            category_pk = None
            category_slug = None
            if self.link_category:
                if isinstance(self.link_category, six.integer_types):
                    category_pk = self.link_category
                elif isinstance(self.link_category, six.string_types):
                    category_slug = self.link_category
            else:
                category_pk = self.kwargs.get('link_category_pk')
                category_slug = self.kwargs.get('link_category_slug')
                if (not category_pk
                        and not category_slug
                        and (self, 'allow_get_parameters', False)):
                    category_slug = (self.request.GET.get('link_category')
                                     or self.request.GET.get('c'))

            try:
                if category_pk:
                    category = LinkCategory.objects.get(pk=category_pk)
                elif category_slug:
                    category = LinkCategory.objects.get(slug=category_slug)
            except LinkCategory.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': LinkCategory._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if category is None and self.require_link_category:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': LinkCategory._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._link_category = category

        return self._link_category

    def get_context_data(self, **kwargs):
        context = super(LinkCategoryMixin, self).get_context_data(**kwargs)
        context['link_category'] = self.get_link_category()
        return context

    def get_queryset(self):
        qs = super(LinkCategoryMixin, self).get_queryset()
        if self.get_link_category():
            qs = qs.filter(**{self.link_category_field: self.get_link_category()})
        return qs

