# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.apps import OverridableConfig


class CommentsConfig(OverridableConfig):
    name = 'marchena.modules.comments'
    verbose_name = _('Comments')

