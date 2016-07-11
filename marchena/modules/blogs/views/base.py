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
        blog = self.get_blog()
        if blog is not None:
            names.insert(-1, '{0}/{1}_detail.html'.format(
                blog._meta.app_label,
                blog._meta.model_name,
            ))
        return names


class BlogListView(ListView):
    """
    Displays a list of blogs.
    """
    model = Blog

    def get_queryset(self):
        model = self.get_model()
        try:
            return model.cache.all()
        except AttributeError:
            return super(BlogListView, self).get_queryset()

