# -*- coding:utf-8 -*-

from yepes.apps import apps

AbstractLink = apps.get_class('links.abstract_models', 'AbstractLink')
AbstractLinkCategory = apps.get_class('links.abstract_models', 'AbstractLinkCategory')


class Link(AbstractLink):
    pass


class LinkCategory(AbstractLinkCategory):
    pass

