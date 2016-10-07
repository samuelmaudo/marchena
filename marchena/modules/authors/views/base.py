# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.view_mixins import CanonicalMixin
from yepes.views import ListView

AuthorMixin = apps.get_class('authors.view_mixins', 'AuthorMixin')
BlogMixin = apps.get_class('blogs.view_mixins', 'BlogMixin')
PostListView = apps.get_class('posts.views', 'PostListView')

Author = apps.get_model('authors', 'Author')


class AuthorDetailView(AuthorMixin, BlogMixin, CanonicalMixin, PostListView):
    """
    Displays a list of published posts that belong to the given author.
    """
    author_field = 'authors'
    require_author = True
    require_blog = False

    def get_canonical_path(self, request):
        author = self.get_author()
        return author.get_absolute_url()

    def get_template_names(self):
        names = super(AuthorDetailView, self).get_template_names()
        author = self.get_author()
        if author is not None:
            names.insert(-1, '{0}/{1}_detail.html'.format(
                author._meta.app_label,
                author._meta.model_name,
            ))
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

