# -*- coding:utf-8 -*-

from django.contrib.auth import get_user_model

User = get_user_model()
UserManager = User._default_manager.__class__


class AuthorManager(UserManager):

    def get_queryset(self):
        qs = super(AuthorManager, self).get_queryset()
        return qs.filter(is_staff=True)

