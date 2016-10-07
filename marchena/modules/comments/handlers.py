# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.text import Truncator

from yepes.contrib.registry import registry
from yepes.loading import LazyClass, LazyModel
from yepes.utils.http import get_meta_data

Comment = LazyModel('comments', 'Comment')
CommentForm = LazyClass('comments.forms', 'CommentForm')


class CommentHandler(object):

    # PUBLIC METHODS

    @classmethod
    def create_comment(cls, post, data, request):

        if not post.allow_comments():
            return None

        author = cls._get_author(request)
        name = data['author_name']
        email = data['author_email']
        url = data['author_url']
        ip_address = cls._get_ip_address(request)
        user_agent = cls._get_user_agent(request)
        referer = cls._get_referer(request)
        content = data['content']

        comment = cls._create_comment(
            post,
            author,
            name,
            email,
            url,
            ip_address,
            user_agent,
            referer,
            content,
        )
        return comment

    @classmethod
    def get_comment_form(cls, post, request):

        if not post.allow_comments():
            return None

        if request.method.upper() in ('POST', 'PUT'):
            kwargs = {
                'data': request.POST,
                'files': request.FILES,
            }
        else:
            kwargs = {}

        return cls._get_comment_form(post, **kwargs)

    # INTERNAL METHODS

    @classmethod
    def _create_comment(cls, post, author, name, email, url, ip_address,
                        user_agent, referer, content):

        comment = Comment(**{
            'post': post,
            'author': author,
            'author_name': name,
            'author_email': email,
            'author_url': url,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'content': Truncator(content).chars(registry['comments:MAX_LENGTH']),
        })
        comment.full_clean()
        comment.save(force_insert=True)
        return comment

    @classmethod
    def _get_author(cls, request):
        try:
            user = request.user
        except AttributeError:
            return None

        try:
            user_is_authenticated = user.is_authenticated()
        except AttributeError:
            return user

        if user_is_authenticated:
            return user
        else:
            return None

    @classmethod
    def _get_comment_form(cls, post, **kwargs):
        return CommentForm(post, **kwargs)

    @classmethod
    def _get_ip_address(cls, request):
        return request.client_ip

    @classmethod
    def _get_referer(cls, request):
        return get_meta_data(request, 'HTTP_REFERER')

    @classmethod
    def _get_user_agent(cls, request):
        return get_meta_data(request, 'HTTP_USER_AGENT')

