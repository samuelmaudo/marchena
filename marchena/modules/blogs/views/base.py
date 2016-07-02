# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps
from yepes.views import ListView

BlogMixin = apps.get_class('blogs.view_mixins', 'BlogMixin')
PostListView = apps.get_class('posts.views', 'PostListView')

Blog = apps.get_model('blogs', 'Blog')


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

