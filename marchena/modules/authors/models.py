# -*- coding:utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from yepes.apps import apps
from yepes.conf import settings
from yepes.model_mixins import Linked
from yepes.urlresolvers import full_reverse

User = apps.get_registered_model(*settings.AUTH_USER_MODEL.split('.'))

AuthorManager = apps.get_class('authors.managers', 'AuthorManager')


@python_2_unicode_compatible
class Author(Linked, User):

    objects = AuthorManager()

    class Meta:
        proxy = True
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    def __str__(self):
        return self.get_full_name() or self.get_username()

    def get_absolute_url(self):
        kwargs = {'author_name': self.get_username()}
        return reverse('post_list', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {'author_name': self.get_username()}
        return full_reverse('post_feed', kwargs=kwargs)

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('username__icontains',
                'first_name__icontains',
                'last_name__icontains')

