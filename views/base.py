# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six
from django.utils.itercompat import is_iterable

from yepes.apps.registry import registry
from yepes.loading import get_model
from yepes.views import DetailView, ListView

from marchena.signals import post_viewed, post_search
from marchena.view_mixins import (
    AuthorMixin,
    BlogMixin,
    CategoryMixin,
    TagMixin,
)
Author = get_model('marchena', 'Author')
Blog = get_model('marchena', 'Blog')
Category = get_model('marchena', 'Category')
Post = get_model('marchena', 'Post')
Tag = get_model('marchena', 'Tag')


class PostDetailView(AuthorMixin, BlogMixin, CategoryMixin, TagMixin, DetailView):
    """
    Displays the details of a published post.
    """

    author_field = 'authors'
    category_field = 'categories'
    guid_url_kwarg = 'post_guid'
    model = Post
    pk_url_kwarg = 'post_pk'
    require_author = False
    require_blog = False
    require_category = False
    require_tag = False
    slug_url_kwarg = 'post_slug'
    tag_field = 'tags'
    view_signal = post_viewed

    def get_queryset(self):
        qs = super(PostDetailView, self).get_queryset()
        qs = qs.published(self.request.user)
        return qs


class PostListView(ListView):
    """
    Displays a list of published posts.
    """
    model = Post

    def get_cache_hash(self, request):
        uri = super(PostListView, self).get_cache_hash(request)
        uri += '&page={0}'.format(request.GET.get('page', 1))
        uri += '&page_size={0}'.format(self.get_paginate_by())
        return uri

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        paginator = context['paginator']
        page = context['page_obj']
        context['page_number'] = page.number if page is not None else 0
        context['page_size'] = paginator.per_page if paginator is not None else 0
        return context

    def get_paginate_by(self, queryset=None):
        if self.paginate_by is None:
            allowed_sizes = [int(s) for s in registry['marchena:DEFAULT_PAGINATION']]
        elif isinstance(self.paginate_by, (list, tuple)):
            allowed_sizes = [int(s) for s in self.paginate_by]
        else:
            allowed_sizes = [int(self.paginate_by)]

        page_size = (self.kwargs.get('paginate_by')
                     or self.request.GET.get('paginate_by')
                     or self.request.GET.get('page_size'))

        if page_size:
            page_size = int(page_size)
        if not page_size or page_size not in allowed_sizes:
            page_size = allowed_sizes[0]

        return page_size

    def get_queryset(self):
        qs = super(PostListView, self).get_queryset()
        qs = qs.published(self.request.user)
        qs = qs.prefetch_related('authors', 'categories', 'images', 'tags')
        return qs


class PostSearchView(AuthorMixin, BlogMixin, CategoryMixin, TagMixin, PostListView):
    """
    Displays a list of published posts filtered by author, blog, category, tag
    or user query.
    """
    allow_get_parameters = True
    author_field = 'authors'
    category_field = 'categories'
    query = None
    require_author = False
    require_blog = False
    require_category = False
    require_tag = False
    search_signal = post_search
    tag_field = 'tags'

    def get_cache_hash(self, request):
        uri = super(PostSearchView, self).get_cache_hash(request)
        if self.get_author():
            uri += '&author={0}'.format(self.get_author().pk)
        if self.get_blog():
            uri += '&blog={0}'.format(self.get_blog().pk)
        if self.get_category():
            uri += '&category={0}'.format(self.get_category().pk)
        if self.get_tag():
            uri += '&tag={0}'.format(self.get_tag().pk)
        if self.get_query():
            uri += '&query={0}'.format(self.get_query())
        return uri

    def get_context_data(self, **kwargs):
        context = super(PostSearchView, self).get_context_data(**kwargs)
        context['query'] = self.get_query()
        return context

    def get_query(self):
        q = (self.query
             or self.kwargs.get('query')
             or self.request.GET.get('query')
             or self.request.GET.get('q'))
        if q is not None:
            return q.strip()
        else:
            return None

    def get_queryset(self):
        qs = super(PostSearchView, self).get_queryset()
        q = self.get_query()
        if q is not None:
            self.send_search_signal(q, self.request)
            return qs.search(q)
        else:
            return qs.none()

    def send_search_signal(self, query, request):
        if self.search_signal is not None:
            self.search_signal.send(
                sender=self,
                query=query,
                request=request)

    def get_template_names(self):
        templates = []
        if isinstance(self.template_name, six.string_types):
            templates.append(self.template_name)
        elif is_iterable(self.template_name):
            templates.extend(self.template_name)

        if self.get_blog() is not None:
            blog = self.get_blog().slug.replace('-', '_')
            templates.extend([
                'marchena/{0}/post_search.html'.format(blog),
                'marchena/{0}/post_list.html'.format(blog),
            ])
        templates.extend([
            'marchena/post_search.html',
            'marchena/post_list.html',
        ])
        return templates

    def get_template_names(self):
        names = super(PostSearchView, self).get_template_names()
        model = self.get_model()
        if model is not None:
            blog = self.get_blog()
            args = (
                model._meta.app_label,
                blog.slug.replace('-', '_') if blog else None,
                model._meta.model_name,
            )
            if blog is not None:
                names.insert(-2, '{0}/{1}/{2}_search.html'.format(*args))

            names.insert(-1, '{0}/{2}_search.html'.format(*args))

        return names


class AuthorDetailView(AuthorMixin, BlogMixin, PostListView):
    """
    Displays a list of published posts that belong to the given author.
    """
    author_field = 'authors'
    require_author = True
    require_blog = False

    def get_template_names(self):
        names = super(AuthorDetailView, self).get_template_names()
        model = self.get_model()
        if model is not None:
            author = self.get_author()
            blog = self.get_blog()
            args = (
                model._meta.app_label,
                blog.slug.replace('-', '_') if blog else None,
                author._meta.model_name,
            )
            if blog is not None:
                names.insert(-2, '{0}/{1}/{2}_detail.html'.format(*args))

            names.insert(-1, '{0}/{2}_detail.html'.format(*args))

        return names


class AuthorListView(BlogMixin, ListView):
    """
    Displays a list of authors.
    """
    blog_field = 'blogs'
    model = Author
    require_blog = False

    def get_queryset(self):
        qs = super(AuthorListView, self).get_queryset()
        return qs.filter(is_active=True)


class BlogDetailView(BlogMixin, PostListView):
    """
    Displays a list of published posts that belong to the given blog.
    """
    require_blog = True

    def get_template_names(self):
        names = super(BlogDetailView, self).get_template_names()
        model = self.get_model()
        if model is not None:
            blog = self.get_blog()
            args = (
                model._meta.app_label,
                blog.slug.replace('-', '_'),
                blog._meta.model_name,
            )
            names.insert(-2, '{0}/{1}/{2}_detail.html'.format(*args))
            names.insert(-1, '{0}/{2}_detail.html'.format(*args))

        return names


class BlogListView(ListView):
    """
    Displays a list of blogs.
    """
    model = Blog

    def get_queryset(self):
        return self.model.cache.all()


class CategoryDetailView(BlogMixin, CategoryMixin, PostListView, ):
    """
    Displays a list of published posts that belong to the given category.
    """
    category_field = 'categories'
    require_blog = True
    require_category = True

    def get_template_names(self):
        names = super(CategoryDetailView, self).get_template_names()
        model = self.get_model()
        if model is not None:
            blog = self.get_blog()
            category = self.get_category()
            args = (
                model._meta.app_label,
                blog.slug.replace('-', '_'),
                category._meta.model_name,
                category.slug.replace('-', '_'),
            )
            names.insert(-2, '{0}/{1}/{2}/{3}.html'.format(*args))
            names.insert(-2, '{0}/{1}/{2}_detail.html'.format(*args))
            names.insert(-1, '{0}/{2}_detail.html'.format(*args))

        return names


class CategoryListView(BlogMixin, ListView):
    """
    Displays a list of categories.
    """
    model = Category
    require_blog = True


class TagDetailView(BlogMixin, TagMixin, PostListView):
    """
    Displays a list of published posts that belong to the given tag.
    """
    require_blog = False
    require_tag = True
    tag_field = 'tags'

    def get_template_names(self):
        names = super(TagDetailView, self).get_template_names()
        model = self.get_model()
        if model is not None:
            tag = self.get_tag()
            blog = self.get_blog()
            args = (
                model._meta.app_label,
                blog.slug.replace('-', '_') if blog else None,
                tag._meta.model_name,
            )
            if blog is not None:
                names.insert(-2, '{0}/{1}/{2}_detail.html'.format(*args))

            names.insert(-1, '{0}/{2}_detail.html'.format(*args))

        return names


class TagListView(BlogMixin, ListView):
    """
    Displays a list of tags.
    """
    blog_field = 'posts__blog'
    model = Tag
    require_blog = False

