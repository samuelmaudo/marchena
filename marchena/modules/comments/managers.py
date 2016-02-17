# -*- coding:utf-8 -*-

from yepes.managers import SearchableManager, SearchableQuerySet


class CommentQuerySet(SearchableQuerySet):
    """
    QuerySet providing main search functionality for ``CommentManager``.
    """

    def published(self):
        """
        Returns published comments.
        """
        return self.filter(is_published=True)


class CommentManager(SearchableManager):

    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)

    def published(self, *args, **kwargs):
        """
        Returns published comments.
        """
        return self.get_queryset().published(*args, **kwargs)

