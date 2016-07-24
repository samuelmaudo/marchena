# -*- coding:utf-8 -*-

from yepes.apps import apps

AbstractCategory = apps.get_class('posts.abstract_models', 'AbstractCategory')
AbstractPost = apps.get_class('posts.abstract_models', 'AbstractPost')
AbstractPostRecord = apps.get_class('posts.abstract_models', 'AbstractPostRecord')
AbstractTag = apps.get_class('posts.abstract_models', 'AbstractTag')


class Category(AbstractCategory):
    pass


class Post(AbstractPost):
    pass


class PostRecord(AbstractPostRecord):
    pass


class Tag(AbstractTag):
    pass

