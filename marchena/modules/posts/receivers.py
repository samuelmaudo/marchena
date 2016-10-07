# -*- coding:utf-8 -*-

from django.db import IntegrityError


def receive_post_view(sender, obj, request, **kwargs):
    """
    Increases the number of times that the post has been viewed.
    """
    if (not kwargs.get('raw', False)
            and (not hasattr(request, 'metrics')
                    or request.metrics.is_tracking)):
        try:
            obj.increase_views_count()
        except IntegrityError:
            pass

