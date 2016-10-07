# -*- coding:utf-8 -*-

from yepes.managers import (
    NestableManager, NestableQuerySet,
    SearchableManager, SearchableQuerySet,
)


class CommentQuerySet(NestableQuerySet, SearchableQuerySet):
    """
    QuerySet providing main search functionality for ``CommentManager``.
    """

    def published(self):
        """
        Returns published comments.
        """
        return self.filter(is_published=True)


class CommentManager(NestableManager, SearchableManager):

    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)

    def published(self, *args, **kwargs):
        """
        Returns published comments.
        """
        return self.get_queryset().published(*args, **kwargs)

