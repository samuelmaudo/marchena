# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.apps import OverridableConfig


class PostsConfig(OverridableConfig):

    name = 'marchena.modules.posts'
    verbose_name = _('Posts')

    def ready(self):
        super(PostsConfig, self).ready()
        post_viewed = self.get_class('signals', 'post_viewed')
        receive_post_view = self.get_class('receivers', 'receive_post_view')
        post_viewed.connect(receive_post_view)

