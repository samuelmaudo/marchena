# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.apps import OverridableConfig


class AuthorsConfig(OverridableConfig):
    name = 'marchena.modules.authors'
    verbose_name = _('Authors')

