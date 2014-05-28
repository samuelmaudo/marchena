# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.syndication.views import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext as _

from yepes.loading import get_model
from yepes.urlresolvers import full_reverse

from marchena.view_mixins import (
    AuthorMixin,
    BlogMixin,
    CategoryMixin,
    TagMixin,
)
Blog = get_model('marchena', 'Blog')
Post = get_model('marchena', 'Post')


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


class PostsRssFeed(Feed):

    model = Post

    def __init__(self, max_items=25, max_words=None):
        self.max_items = max_items
        self.max_words = max_words

    def get_object(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return None

    def get_queryset(self):
        return self.model._default_manager.published() \
                                          .prefetch_related('authors') \
                                          .order_by('-publish_from')

    def title(self):
        return _('Posts')

    def link(self):
        return full_reverse('post_list')

    def description(self):
        return _('Latest published posts.')

    def items(self):
        qs = self.get_queryset()
        if self.max_items:
            qs = qs[:self.max_items]
        return qs.iterator()

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.get_full_url()

    def item_description(self, item):
        if self.max_words:
            return item.get_excerpt(max_words)
        else:
            return item.get_content()

    def item_author_name(self, item):
        authors = [
            (a.get_full_name()
             or a.get_username())
            for a
            in item.authors.all()
        ]
        coordinator = ' {0} '.format(_('and'))
        authors[-2:] = [coordinator.join(authors[-2:])]
        return ', '.join(authors)

    def item_pubdate(self, item):
        return item.publish_from or item.creation_date


class PostsAtomFeed(PostsRssFeed):
    feed_type = Atom1Feed


class AuthorPostsRssFeed(AuthorMixin, BlogMixin, PostsRssFeed):

    author_field = 'authors'
    require_author = True
    require_blog = False

    def get_object(self, *args, **kwargs):
        super(AuthorPostsRssFeed, self).get_object(*args, **kwargs)
        a = self.get_author()
        b = self.get_blog()
        return (a, b)

    def title(self, obj):
        author, blog = obj
        if blog is None:
            context = {'author': author}
            template = _("{author}'s posts")
        else:
            context = {'author': author, 'blog': blog}
            template = _("{author}'s posts on {blog}")
        return template.format(**context)

    def link(self, obj):
        author, blog = obj
        kwargs = {
            #'author_pk': author.pk,
            'author_name': author.get_username(),
        }
        if blog is not None:
            kwargs.update({
                #'blog_pk': blog.pk,
                'blog_slug': blog.slug,
            })
        return full_reverse('post_list', kwargs=kwargs)

    def description(self, obj):
        author, blog = obj
        if blog is None:
            context = {'author': author}
            template = _('Latest posts authored by "{author}".')
        else:
            context = {'author': author, 'blog': blog}
            template = _('Latest posts authored by "{author}" on "{blog}".')
        return template.format(**context)


class AuthorPostsAtomFeed(AuthorPostsRssFeed):
    feed_type = Atom1Feed


class BlogPostsRssFeed(BlogMixin, PostsRssFeed):

    require_blog = True

    def get_object(self, *args, **kwargs):
        super(BlogPostsRssFeed, self).get_object(*args, **kwargs)
        return self.get_blog()

    def title(self, obj):
        return obj.title

    def link(self, obj):
        kwargs = {
            #'blog_pk': obj.pk,
            'blog_slug': obj.slug,
        }
        return full_reverse('post_list', kwargs=kwargs)

    def description(self, obj):
        context = {'blog': obj}
        template = _('Latest posts on "{blog}".')
        return template.format(**context)


class BlogPostsAtomFeed(BlogPostsRssFeed):
    feed_type = Atom1Feed


class CategoryPostsRssFeed(BlogMixin, CategoryMixin, PostsRssFeed):

    category_field = 'categories'
    require_blog = True
    require_category = True

    def get_object(self, *args, **kwargs):
        super(CategoryPostsRssFeed, self).get_object(*args, **kwargs)
        b = self.get_blog()
        c = self.get_category()
        return (b, c)

    def title(self, obj):
        blog, category= obj
        context = {'blog': blog, 'category': category}
        template = _('{category} on {blog}')
        return template.format(**context)

    def link(self, obj):
        blog, category= obj
        kwargs = {
            #'blog_pk': blog.pk,
            'blog_slug': blog.slug,
            #'category_pk': category.pk,
            'category_slug': category.slug,
        }
        return full_reverse('post_list', kwargs=kwargs)

    def description(self, obj):
        blog, category= obj
        context = {'blog': blog, 'category': category}
        template = _('Latest posts from "{category}" on "{blog}".')
        return template.format(**context)


class CategoryPostsAtomFeed(CategoryPostsRssFeed):
    feed_type = Atom1Feed


class TagPostsRssFeed(BlogMixin, TagMixin, PostsRssFeed):

    require_blog = False
    require_tag = True
    tag_field = 'tags'

    def get_object(self, *args, **kwargs):
        super(TagPostsRssFeed, self).get_object(*args, **kwargs)
        b = self.get_blog()
        t = self.get_tag()
        return (b, t)

    def title(self, obj):
        blog, tag= obj
        if blog is None:
            context = {'tag': tag}
            template = _('{tag}')
        else:
            context = {'blog': blog, 'tag': tag}
            template = _('{tag} on {blog}')
        return template.format(**context)

    def link(self, obj):
        blog, tag= obj
        kwargs = {
            #'tag_pk': tag.pk,
            'tag_slug': tag.slug,
        }
        if blog is not None:
            kwargs.update({
                #'blog_pk': blog.pk,
                'blog_slug': blog.slug,
            })
        return full_reverse('post_list', kwargs=kwargs)

    def description(self, obj):
        blog, tag= obj
        if blog is None:
            context = {'tag': tag}
            template = _('Latest posts from "{tag}".')
        else:
            context = {'blog': blog, 'tag': tag}
            template = _('Latest posts from "{tag}" on "{blog}".')
        return template.format(**context)


class TagPostsAtomFeed(TagPostsRssFeed):
    feed_type = Atom1Feed
