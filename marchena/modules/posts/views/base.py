# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.loading import get_class, get_model
from yepes.views import DetailView, ListView

from marchena.modules.posts.signals import post_viewed, post_search

AuthorMixin = get_class('authors.view_mixins', 'AuthorMixin')
BlogMixin = get_class('blogs.view_mixins', 'BlogMixin')
CategoryMixin = get_class('posts.view_mixins', 'CategoryMixin')
TagMixin = get_class('posts.view_mixins', 'TagMixin')

Category = get_model('posts', 'Category')
Post = get_model('posts', 'Post')
Tag = get_model('posts', 'Tag')


class PostDetailView(AuthorMixin, BlogMixin, CategoryMixin, TagMixin, DetailView):
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

    def get_queryset(self):
        qs = super(PostListView, self).get_queryset()
        qs = qs.published(self.request.user)
        qs = qs.prefetch_related('authors', 'categories', 'tags')
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


class CategoryDetailView(BlogMixin, CategoryMixin, PostListView):
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

