# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.loading import get_class, get_model
from yepes.views import ListView

AuthorMixin = get_class('authors.view_mixins', 'AuthorMixin')
BlogMixin = get_class('blogs.view_mixins', 'BlogMixin')
PostListView = get_class('posts.views', 'PostListView')

Author = get_model('authors', 'Author')


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

