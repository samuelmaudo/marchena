# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils import six
from django.utils.translation import ugettext as _

from yepes.loading import get_model
from yepes.types import Undefined

Author = get_model('authors', 'Author')
AuthorManager = Author._default_manager


class AuthorMixin(object):

    _author = Undefined
    author = None
    author_field = 'author'
    require_author = False

    def get_author(self):
        if self._author is Undefined:

            author = None
            author_pk = None
            author_name = None
            if self.author:
                if isinstance(self.author, six.integer_types):
                    author_pk = self.author
                elif isinstance(self.author, six.string_types):
                    author_name = self.author
            else:
                author_pk = self.kwargs.get('author_pk')
                author_name = self.kwargs.get('author_name')
                if (not author_pk
                        and not author_name
                        and (self, 'allow_get_parameters', False)):
                    author_name = (self.request.GET.get('author')
                                   or self.request.GET.get('a'))

            authors = AuthorManager.filter(is_active=True)
            try:
                if author_pk:
                    author = authors.get(pk=author_pk)
                elif author_name:
                    field = Author.USERNAME_FIELD
                    author = authors.get(**{field: author_name})
            except Author.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': Author._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if author is None and self.require_author:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': Author._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._author = author

        return self._author

    def get_context_data(self, **kwargs):
        context = super(AuthorMixin, self).get_context_data(**kwargs)
        context['author'] = self.get_author()
        return context

    def get_queryset(self):
        qs = super(AuthorMixin, self).get_queryset()
        if self.get_author():
            qs = qs.filter(**{self.author_field: self.get_author()})
        return qs

