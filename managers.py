# -*- coding:utf-8 -*-

from django.contrib.auth import get_user_model

from yepes.managers import SearchableManager, SearchableQuerySet

User = get_user_model()
UserManager = User._default_manager.__class__


class AuthorManager(UserManager):

    def get_queryset(self):
        qs = super(AuthorManager, self).get_queryset()
        return qs.filter(is_staff=True)


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

