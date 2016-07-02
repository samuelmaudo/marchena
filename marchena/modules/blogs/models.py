# -*- coding:utf-8 -*-

from yepes.apps import apps

AbstractBlog = apps.get_class('blogs.abstract_models', 'AbstractBlog')


class Blog(AbstractBlog):
    pass

