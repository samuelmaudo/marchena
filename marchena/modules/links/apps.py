# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.apps import OverridableConfig


class LinksConfig(OverridableConfig):
    name = 'marchena.modules.links'
    verbose_name = _('Links')

