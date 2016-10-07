# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils import six
from django.utils.translation import ugettext as _

from yepes.apps import apps
from yepes.types import Undefined

Blog = apps.get_model('blogs', 'Blog')


class BlogMixin(object):

    _blog = Undefined
    blog = None
    blog_field = 'blog'
    require_blog = False

    def get_blog(self):
        if self._blog is Undefined:

            blog = None
            blog_pk = None
            blog_slug = None
            if not self.blog:
                blog_pk = self.kwargs.get('blog_pk')
                blog_slug = self.kwargs.get('blog_slug')
            elif isinstance(self.blog, six.integer_types):
                blog_pk = self.blog
            elif isinstance(self.blog, six.string_types):
                blog_slug = self.blog

            if blog_pk:
                blog = Blog.cache.get(blog_pk)
                if blog is None:
                    msg = _('No {verbose_name} found matching the query.')
                    kwargs = {'verbose_name': Blog._meta.verbose_name}
                    raise Http404(msg.format(**kwargs))

            elif blog_slug:
                blog = Blog.cache.get(slug=blog_slug)
                if blog is None:
                    msg = _('No {verbose_name} found matching the query.')
                    kwargs = {'verbose_name': Blog._meta.verbose_name}
                    raise Http404(msg.format(**kwargs))

            elif self.require_blog:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': Blog._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._blog = blog

        return self._blog

    def get_context_data(self, **kwargs):
        context = super(BlogMixin, self).get_context_data(**kwargs)
        context['blog'] = self.get_blog()
        return context

    def get_queryset(self):
        qs = super(BlogMixin, self).get_queryset()
        if self.get_blog():
            qs = qs.filter(**{self.blog_field: self.get_blog()})
        return qs

    def get_template_names(self):
        names = super(BlogMixin, self).get_template_names()
        blog = self.get_blog()
        if blog is not None:
            model = self.get_model()
            if model is not None:
                args = (
                    model._meta.app_label,
                    blog.slug.replace('-', '_'),
                    model._meta.model_name,
                    self.template_name_suffix,
                )
                names.insert(-1, '{0}/{1}/{2}{3}.html'.format(*args))

        return names

