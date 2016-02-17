# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.registry import Registry
from yepes.contrib.registry.fields import *


registry = Registry(namespace='marchena')
registry.register(
    'COMMENTS_ANCHOR_PATTERN',
    CharField(
        initial = '#c{id}',
        label = 'Plantilla de ancla para los comentarios.',
        max_length = 31,
        required = True,
))
registry.register(
    'COMMENTS_DAYS_ALLOWED',
    IntegerField(
        initial = 30,
        label = 'Número de días para añadir nuevos comentarios.',
        help_text = 'Si el valor es cero, no habrá ningún límite.',
        min_value = 0,
        required = False,
))
registry.register(
    'COMMENTS_INITIAL_STATUS',
    ModelChoiceField(
        initial = 1,
        label = 'Estado inicial',
        model = 'marchena.CommentStatus',
        required = True,
))
registry.register(
    'DEFAULT_PAGINATION',
    CommaSeparatedField(
        initial = ('9', '18', '27'),
        label = 'Número de artículos por página',
        max_length = 255,
        required = True,
))

