# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import template
from django.contrib.admin.options import IS_POPUP_VAR, TO_FIELD_VAR
from django.contrib.admin.utils import quote
from django.core.urlresolvers import get_script_prefix, resolve, Resolver404
from django.utils.http import urlencode
from django.utils.six.moves.urllib.parse import parse_qsl, urlparse, urlunparse

register = template.Library()


@register.filter
def desk_urlname(value, arg):
    return 'desk:{0}_{1}_{2}'.format(value.app_label, value.model_name, arg)


@register.filter
def desk_urlquote(value):
    return quote(value)


@register.simple_tag(takes_context=True)
def add_preserved_filters(context, url, popup=False, to_field=None):
    opts = context.get('opts')
    preserved_filters = context.get('preserved_filters')

    parsed_url = list(urlparse(url))
    parsed_qs = dict(parse_qsl(parsed_url[4]))
    merged_qs = dict()

    if opts and preserved_filters:
        preserved_filters = dict(parse_qsl(preserved_filters))

        match_url = '/{0}'.format(url.partition(get_script_prefix())[2])
        try:
            match = resolve(match_url)
        except Resolver404:
            pass
        else:
            current_url = '{0}:{1}'.format(match.app_name, match.url_name)
            changelist_url = 'desk:{0}_{1}_changelist'.format(opts.app_label, opts.model_name)
            if (current_url == changelist_url
                    and '_changelist_filters' in preserved_filters):
                preserved_filters = dict(parse_qsl(preserved_filters['_changelist_filters']))

        merged_qs.update(preserved_filters)

    if popup:
        merged_qs[IS_POPUP_VAR] = 1

    if to_field:
        merged_qs[TO_FIELD_VAR] = to_field

    merged_qs.update(parsed_qs)

    parsed_url[4] = urlencode(merged_qs)
    return urlunparse(parsed_url)

