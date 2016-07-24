# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.template import Library

from yepes.apps import apps
from yepes.template import AssignTag, MultipleObjectMixin, SingleObjectMixin

Author = apps.get_model('authors', 'Author')

register = Library()


## {% get_author username **options[ as variable_name] %} ######################


class GetAuthorTag(SingleObjectMixin, AssignTag):

    assign_var = False
    field_name = Author.USERNAME_FIELD
    model = Author

    def process(self, username, **options):
        qs = self.get_queryset()
        qs = qs.filter(is_active=True)
        if options.get('blogs'):
            qs = qs.prefetch_related('blogs')

        if options.get('posts'):
            qs = qs.prefetch_related('posts')

        return self.get_object(qs, username)

register.tag('get_author', GetAuthorTag.as_tag())


## {% get_authors *usernames **options as variable_name %} #####################


class GetAuthorsTag(MultipleObjectMixin, AssignTag):

    field_name = Author.USERNAME_FIELD
    model = Author

    def process(self, *usernames, **options):
        qs = self.get_queryset()
        qs = qs.filter(is_active=True)
        if options.get('blogs'):
            qs = qs.prefetch_related('blogs')

        if options.get('posts'):
            qs = qs.prefetch_related('posts')

        return self.get_object_list(qs, usernames)

register.tag('get_authors', GetAuthorsTag.as_tag())

