# -*- coding:utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from yepes.apps import apps
from yepes.conf import settings
from yepes.urlresolvers import build_full_url, full_reverse

from marchena.modules.authors.managers import AuthorManager

User = apps.get_registered_model(*settings.AUTH_USER_MODEL.split('.'))


@python_2_unicode_compatible
class Author(User):

    objects = AuthorManager()

    class Meta:
        proxy = True
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    def get_absolute_url(self):
        kwargs = {
            #'author_pk': self.pk,
            'author_name': self.get_username(),
        }
        return reverse('post_list', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {
            #'author_pk': self.pk,
            'author_name': self.get_username(),
        }
        return full_reverse('post_feed', kwargs=kwargs)

    def get_full_url(self):
        return build_full_url(self.get_absolute_url())

    def get_link(self):
        return mark_safe('<a href="{0}">{1}</a>'.format(
                         self.get_absolute_url(),
                         self))

    def __str__(self):
        return self.get_full_name() or self.get_username()

