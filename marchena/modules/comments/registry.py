# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.contrib.registry import Registry
from yepes.contrib.registry.fields import *


registry = Registry(namespace='comments')
registry.register(
    'INITIAL_STATUS',
    ModelChoiceField(
        initial = 1,
        label = _('Initial comment status'),
        model = 'comments.CommentStatus',
        required = True,
))
registry.register(
    'MAX_DAYS',
    IntegerField(
        initial = 0,
        label = _('Limit of days'),
        help_text = _('Automatically close comments on posts older than this number of days. If value is zero, there will be no limit.'),
        min_value = 0,
        required = False,
))
registry.register(
    'MAX_LENGTH',
    IntegerField(
        initial = 3000,
        label = _('Limit of characters'),
        help_text = _('Forbid to add comments longer than this number of characters. If value is zero, there will be no limit.'),
        min_value = 0,
        required = False,
))
registry.register(
    'REQUIRE_EMAIL',
    BooleanField(
        initial = True,
        label = _('Require e-mail'),
        help_text = _('Comment author must fill out name and e-mail.'),
        required = False,
))
registry.register(
    'REQUIRE_LOGIN',
    BooleanField(
        initial = False,
        label = _('Require login'),
        help_text = _('Users must be registered and logged in to comment.'),
        required = False,
))
