# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.contrib.registry import Registry
from yepes.contrib.registry.fields import *


registry = Registry(namespace='posts')
registry.register(
    'ALLOW_COMMENTS',
    BooleanField(
        initial = True,
        label = _('Allow comments'),
        help_text = _('Default value for new posts.'),
        required = False,
))
registry.register(
    'PAGINATION_SIZES',
    CommaSeparatedField(
        initial = ('12', ),
        label = _('Posts per page'),
        max_length = 255,
        required = True,
))

