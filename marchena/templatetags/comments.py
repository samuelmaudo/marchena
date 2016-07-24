# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.template import Library
from django.utils import six

from yepes.apps import apps
from yepes.template import AssignTag, InclusionTag, MultipleObjectMixin

Author = apps.get_model('authors', 'Author')
Comment = apps.get_model('comments', 'Comment')

register = Library()


## {% get_recent_comments[ limit[ status[ user[ blog]]]] as var %} #############


class GetRecentCommentsTag(MultipleObjectMixin, AssignTag):

    model = Comment

    def process(self, limit=5, status=None, user=None, blog=None):
        qs = self.get_queryset()
        qs = qs.order_by('-creation_date')

        if status is None:
            qs = qs.published()
        elif isinstance(status, six.string_types):
            qs = qs.filter(status__api_id=status)
        else:
            qs = qs.filter(status=status)

        if user is not None:
            if isinstance(user, six.string_types):
                username_lookup = 'user__{0}'.format(Author.USERNAME_FIELD)
                qs = qs.filter(**{username_lookup: user})
            else:
                qs = qs.filter(user=user)

        if blog is not None:
            if isinstance(blog, six.string_types):
                qs = qs.filter(post__blog__slug=blog)
            else:
                qs = qs.filter(post__blog=blog)

        if limit:
            qs = qs[:limit]

        return qs

register.tag('get_recent_comments', GetRecentCommentsTag.as_tag())


## {% post_comments[ limit[ status[ order_by]]] %} #############################


class PostCommentsTag(InclusionTag):

    template = 'partials/comments.html'

    def process(self, limit=None, status=None, order_by=None):
        post = self.context.get('post')
        if not post:
            return ''

        context = self.get_new_context()
        context.update({
            'post': post,
            'comment_list': post.get_comments(limit, status, order_by),
            'form': None,
        })
        return self.get_content(context)

register.tag('post_comments', PostCommentsTag.as_tag())

