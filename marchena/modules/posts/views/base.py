# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.http import HttpResponseRedirect

from yepes.apps import apps
from yepes.conf import settings
from yepes.contrib.registry import registry
from yepes.view_mixins import CanonicalMixin
from yepes.views import DetailView, ListView, SearchView
from yepes.types import Undefined

from marchena.modules.posts.signals import post_search, post_viewed

CommentHandler = apps.get_class('comments.handlers', 'CommentHandler')

AuthorMixin = apps.get_class('authors.view_mixins', 'AuthorMixin')
BlogMixin = apps.get_class('blogs.view_mixins', 'BlogMixin')
CategoryMixin = apps.get_class('posts.view_mixins', 'CategoryMixin')
TagMixin = apps.get_class('posts.view_mixins', 'TagMixin')

Category = apps.get_model('posts', 'Category')
Post = apps.get_model('posts', 'Post')
Tag = apps.get_model('posts', 'Tag')


class PostDetailView(AuthorMixin, BlogMixin, CategoryMixin, DetailView):
    """
    Displays the details of a published post.
    """
    author_field = 'authors'
    category_field = 'categories'
    model = Post
    pk_url_kwarg = 'post_pk'
    require_author = False
    require_blog = False
    require_category = False
    slug_url_kwarg = 'post_slug'
    view_signal = post_viewed

    def form_valid(self, form):
        CommentHandler.create_comment(
            post=self.object,
            data=form.get_comment_data(),
            request=self.request,
        )
        return HttpResponseRedirect(self.object.get_absolute_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(comment_form=form))

    def get_context_data(self, **kwargs):
        kwargs = super(PostDetailView, self).get_context_data(**kwargs)
        if 'comment_form' not in kwargs:
            kwargs['comment_form'] = self.get_form()
        return kwargs

    def get_form(self):
        form = CommentHandler.get_comment_form(
            post=self.object,
            request=self.request,
        )
        return form

    def get_queryset(self):
        qs = super(PostDetailView, self).get_queryset()
        qs = qs.published(self.request.user)
        return qs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class PostListMixin(object):

    model = Post

    def get_page_sizes(self):
        if self._page_sizes is Undefined:
            sizes = super(PostListMixin, self).get_page_sizes()
            if not sizes:
                sizes = registry['posts:PAGINATION_SIZES']
                self._page_sizes = self.normalize_page_sizes(sizes)

        return self._page_sizes

    def get_queryset(self):
        qs = super(PostListMixin, self).get_queryset()
        qs = qs.published(self.request.user)
        qs = qs.prefetch_related('authors', 'categories', 'tags')
        return qs


class PostListView(PostListMixin, ListView):
    """
    Displays a list of published posts.
    """


class PostSearchView(PostListMixin, SearchView):
    """
    Displays a list of published posts.

    Optionally, user can filter posts by query.

    """
    search_signal = post_search


class CategoryDetailView(BlogMixin, CategoryMixin, CanonicalMixin, PostListView):
    """
    Displays a list of published posts that belong to the given category.
    """
    category_field = 'categories'
    require_blog = settings.BLOG_MULTIPLE
    require_category = True

    def get_canonical_path(self, request):
        category = self.get_category()
        return category.get_absolute_url()

    def get_template_names(self):
        names = super(CategoryDetailView, self).get_template_names()
        category = self.get_category()
        if category is not None:
            names.insert(-1, '{0}/{1}_detail.html'.format(
                category._meta.app_label,
                category._meta.model_name,
            ))
        return names


class CategoryListView(BlogMixin, ListView):
    """
    Displays a list of categories.
    """
    model = Category
    require_blog = settings.BLOG_MULTIPLE


class TagDetailView(BlogMixin, TagMixin, CanonicalMixin, PostListView):
    """
    Displays a list of published posts that belong to the given tag.
    """
    require_blog = False
    require_tag = True
    tag_field = 'tags'

    def get_canonical_path(self, request):
        tag = self.get_tag()
        return tag.get_absolute_url()

    def get_template_names(self):
        names = super(TagDetailView, self).get_template_names()
        tag = self.get_tag()
        if tag is not None:
            names.insert(-1, '{0}/{1}_detail.html'.format(
                tag._meta.app_label,
                tag._meta.model_name,
            ))
        return names


class TagListView(BlogMixin, ListView):
    """
    Displays a list of tags.
    """
    blog_field = 'posts__blog'
    model = Tag
    require_blog = False

