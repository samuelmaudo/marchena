# -*- coding:utf-8 -*-

from yepes.apps import apps

AbstractComment = apps.get_class('comments.abstract_models', 'AbstractComment')
AbstractCommentStatus = apps.get_class('comments.abstract_models', 'AbstractCommentStatus')


class Comment(AbstractComment):
    pass


class CommentStatus(AbstractCommentStatus):
    pass

