# -*- coding:utf-8 -*-

from django.dispatch import Signal

post_viewed = Signal(providing_args=[
    'obj',
    'request',
    'response',
])
post_search = Signal(providing_args=[
    'query',
    'request',
])
