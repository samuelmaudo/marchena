# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from django.db.models import F, Q
from django.template import Library
from django.utils import six
from django.utils import timezone

from yepes.apps import apps
from yepes.template import AssignTag, InclusionTag
from yepes.template import MultipleObjectMixin, SingleObjectMixin
from yepes.types import Undefined

Author = apps.get_model('authors', 'Author')
Comment = apps.get_model('comments', 'Comment')
CommentForm = apps.get_class('comments.forms', 'CommentForm')

register = Library()


## {% comment_form[ post[ form]] %} ############################################


class CommentFormTag(InclusionTag):

    template = 'partials/comment_form.html'

    def process(self, post=None, form=Undefined):
        if post is None:
            post = self.context.get('post')
            if not post:
                return ''

        if form is Undefined:
            form = self.context.get('comment_form')

        context = self.get_new_context()
        context.update({
            'post': post,
            'comment_form': form,
        })
        return self.get_content(context)

register.tag('comment_form', CommentFormTag.as_tag())


## {% get_comment comment_id[ as variable_name] %} #############################


class GetCommentTag(SingleObjectMixin, AssignTag):

    field_name = 'pk'
    model = Comment
    target_var = 'comment'

    def process(self, comment_id):
        qs = self.get_queryset()
        return self.get_object(qs, comment_id)

register.tag('get_comment', GetCommentTag.as_tag())


## {% get_comments[ limit[ status[ ordering[ author[ blog[ category[ tag[ days]]]]]]]][ as variable_name] %} #####


class GetCommentsTag(MultipleObjectMixin, AssignTag):

    model = Comment
    target_var = 'comment_list'

    def get_queryset(self):
        qs = super(GetCommentsTag, self).get_queryset()
        qs = qs.prefetch_related('author', 'post')
        return qs

    def process(self, limit=5, status=None, ordering='creation_date',
                      author=None, blog=None, category=None, tag=None,
                      days=None):

        qs = self.get_queryset()
        qs = qs.order_by(ordering)

        if status is None:
            qs = qs.published()
        elif isinstance(status, six.string_types):
            qs = qs.filter(status__api_id=status)
        else:
            qs = qs.filter(status=status)

        if author is not None:
            if isinstance(author, six.string_types):
                username_lookup = 'user__{0}'.format(Author.USERNAME_FIELD)
                qs = qs.filter(Q(author_email=author)
                               | Q(user__email=author)
                               | Q(**{username_lookup: author}))
            elif isinstance(author, six.integer_types):
                qs = qs.filter(user_id=author)
            else:
                qs = qs.filter(user=author)

        if blog is not None:
            if isinstance(blog, six.string_types):
                qs = qs.filter(post__blog__slug=blog)
            elif isinstance(blog, six.integer_types):
                qs = qs.filter(post__blog_id=blog)
            else:
                qs = qs.filter(post__blog=blog)

        if category is not None:
            if isinstance(category, six.string_types):
                qs = qs.filter(post__categories__slug=category)
            elif isinstance(category, six.integer_types):
                qs = qs.filter(post__categories__pk=category)
            else:
                qs = qs.filter(post__categories=category)

        if tag is not None:
            if isinstance(tag, six.string_types):
                qs = qs.filter(post__tags__slug=tag)
            elif isinstance(tag, six.integer_types):
                qs = qs.filter(post__tags__pk=tag)
            else:
                qs = qs.filter(post__tags=tag)

        if days is not None:
            date = timezone.now() - timedelta(days=days)
            qs = qs.filter(creation_date__gte=date)

        if limit:
            qs = qs[:limit]

        return qs

register.tag('get_comments', GetCommentsTag.as_tag())


## {% get_popular_comments[ limit[ status[ author[ blog[ category[ tag[ days]]]]]]][ as variable_name] %} #####


class GetPopularCommentsTag(GetCommentsTag):

    def process(self, limit=5, status=None, author=None, blog=None, category=None, tag=None, days=30):
        ordering='-karma'
        return self.super_process(limit, status, ordering, author, blog, category, tag, days)

register.tag('get_popular_comments', GetPopularCommentsTag.as_tag())


## {% get_recent_comments[ limit[ status[ author[ blog[ category[ tag]]]]]][ as variable_name] %} #####


class GetRecentCommentsTag(GetCommentsTag):

    def process(self, limit=5, status=None, author=None, blog=None, category=None, tag=None):
        ordering='-creation_date'
        days = None
        return self.super_process(limit, status, ordering, author, blog, category, tag, days)

register.tag('get_recent_comments', GetRecentCommentsTag.as_tag())


## {% get_post_comments[ limit[ status[ ordering[ post]]]][ as variable_name] %} #####


class GetPostCommentsTag(AssignTag):

    target_var = 'comment_list'

    def process(self, limit=None, status=None, ordering=None, post=None):
        if post is None:
            post = self.context.get('post')
            if not post:
                return ''

        return post.get_comments(limit, status, ordering)

register.tag('get_post_comments', GetPostCommentsTag.as_tag())


## {% post_comments[ limit[ status[ ordering[ post[ form]]]] %} ################


class PostCommentsTag(InclusionTag):

    template = 'partials/comment_list.html'

    def process(self, limit=None, status=None, ordering=None, post=None,
                      form=Undefined):

        if post is None:
            post = self.context.get('post')
            if not post:
                return ''

        if form is Undefined:
            form = self.context.get('comment_form')

        context = self.get_new_context()
        context.update({
            'post': post,
            'comment_form': form,
            'comment_list': post.get_comments(limit, status, ordering),
        })
        return self.get_content(context)

register.tag('post_comments', PostCommentsTag.as_tag())

