# -*- coding:utf-8 -*-

from yepes.apps import apps
from yepes.conf import settings

User = apps.get_registered_model(*settings.AUTH_USER_MODEL.split('.'))
UserManager = User._default_manager.__class__


class AuthorManager(UserManager):

    def get_queryset(self):
        qs = super(AuthorManager, self).get_queryset()
        return qs.filter(is_staff=True)

