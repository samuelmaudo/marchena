# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.syndication.views import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext as _

from yepes.loading import get_model

Blog = get_model('blogs', 'Blog')
Post = get_model('posts', 'Post')


class CommentRssFeed(Feed):

    def __init__(self, max_items=25, max_words=None):
        self.max_items = max_items
        self.max_words = max_words

    def get_object(self, request, blog_pk=None, blog_slug=None,
                   post_pk=None, post_slug=None):

        if blog_pk:
            blog = Blog.cache.get(pk=blog_pk)
        elif blog_slug:
            blog = Blog.cache.get(slug=blog_slug)
        else:
            msg = _('You must specify a {verbose_name}.')
            raise Http404(msg.format(verbose_name=Blog._meta.verbose_name))
        if blog is None:
            msg = _('No {verbose_name} found matching the query.')
            raise Http404(msg.format(verbose_name=Blog._meta.verbose_name))

        try:
            if post_pk:
                post = blog.posts.published().get(pk=post_pk)
            elif post_slug:
                post = blog.posts.published().get(slug=post_slug)
            else:
                post = None
        except ObjectDoesNotExist:
            msg = _('No {verbose_name} found matching the query.')
            raise Http404(msg.format(verbose_name=Post._meta.verbose_name))

        if post is not None:
            return post
        else:
            return blog

    def title(self, obj):
        if isinstance(obj, Blog):
            t = _('Latest comments on "{blog_title}"')
            return t.format(blog_title=obj.title)
        else:
            t = _('Comments to "{post_title}"')
            return t.format(post_title=obj.title)

    def link(self, obj):
        return obj.get_full_url()

    def description(self, obj):
        d = _('Last {max_items} comments to "{obj_title}"')
        return d.format(max_items=self.max_items, obj_title=obj.title)

    def items(self, obj):
        qs = obj.comments.published() \
                         .select_related('post', 'author') \
                         .order_by('-creation_date')
        if self.max_items:
            qs = qs[:self.max_items]
        return qs.iterator()

    def item_title(self, item):
        return item.post.title

    def item_link(self, item):
        return item.get_full_url()

    def item_description(self, item):
        if self.max_words:
            return item.get_excerpt(max_words)
        else:
            return item.get_content()

    def item_author_name(self, item):
        return item.get_author_name()

    def item_pubdate(self, item):
        return item.creation_date


class CommentAtomFeed(CommentRssFeed):
    feed_type = Atom1Feed

