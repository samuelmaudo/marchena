# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils import six
from django.utils.translation import ugettext as _

from yepes.loading import get_model
from yepes.types import Undefined

Author = get_model('marchena', 'Author')
AuthorManager = Author._default_manager
Blog = get_model('marchena', 'Blog')
BlogManager = Blog._default_manager
Category = get_model('marchena', 'Category')
CategoryManager = Category._default_manager
Tag = get_model('marchena', 'Tag')
TagManager = Tag._default_manager


class AuthorMixin(object):

    _author = Undefined
    author = None
    author_field = 'author'
    require_author = False

    def get_author(self):
        if self._author is Undefined:

            author = None
            author_pk = None
            author_name = None
            if self.author:
                if isinstance(self.author, six.integer_types):
                    author_pk = self.author
                elif isinstance(self.author, six.string_types):
                    author_name = self.author
            else:
                author_pk = self.kwargs.get('author_pk')
                author_name = self.kwargs.get('author_name')
                if (not author_pk
                        and not author_name
                        and (self, 'allow_get_parameters', False)):
                    author_name = (self.request.GET.get('author')
                                   or self.request.GET.get('a'))

            authors = AuthorManager.filter(is_active=True)
            try:
                if author_pk:
                    author = authors.get(pk=author_pk)
                elif author_name:
                    field = Author.USERNAME_FIELD
                    author = authors.get(**{field: author_name})
            except Author.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': Author._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if author is None and self.require_author:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': Author._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._author = author

        return self._author

    def get_context_data(self, **kwargs):
        context = super(AuthorMixin, self).get_context_data(**kwargs)
        context['author'] = self.get_author()
        return context

    def get_queryset(self):
        qs = super(AuthorMixin, self).get_queryset()
        if self.get_author():
            qs = qs.filter(**{self.author_field: self.get_author()})
        return qs


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
            if self.blog:
                if isinstance(self.blog, six.integer_types):
                    blog_pk = self.blog
                elif isinstance(self.blog, six.string_types):
                    blog_slug = self.blog
            else:
                blog_pk = self.kwargs.get('blog_pk')
                blog_slug = self.kwargs.get('blog_slug')
                if (not blog_pk
                        and not blog_slug
                        and (self, 'allow_get_parameters', False)):
                    blog_slug = (self.request.GET.get('blog')
                                 or self.request.GET.get('b'))

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


class CategoryMixin(object):

    _category = Undefined
    category = None
    category_field = 'category'
    require_category = False

    def get_category(self):
        if self._category is Undefined:

            category = None
            category_pk = None
            category_slug = None
            if self.category:
                if isinstance(self.category, six.integer_types):
                    category_pk = self.category
                elif isinstance(self.category, six.string_types):
                    category_slug = self.category
            else:
                category_pk = self.kwargs.get('category_pk')
                category_slug = self.kwargs.get('category_slug')
                if (not category_pk
                        and not category_slug
                        and (self, 'allow_get_parameters', False)):
                    category_slug = (self.request.GET.get('category')
                                     or self.request.GET.get('c'))

            try:
                if category_pk:
                    category = CategoryManager.get(pk=category_pk)
                elif category_slug:
                    category = CategoryManager.get(slug=category_slug)
            except Category.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': Category._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if category is None and self.require_category:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': Category._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._category = category

        return self._category

    def get_context_data(self, **kwargs):
        context = super(CategoryMixin, self).get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context

    def get_queryset(self):
        qs = super(CategoryMixin, self).get_queryset()
        if self.get_category():
            qs = qs.filter(**{self.category_field: self.get_category()})
        return qs


class TagMixin(object):

    _tag = Undefined
    tag = None
    tag_field = 'tag'
    require_tag = False

    def get_tag(self):
        if self._tag is Undefined:

            tag = None
            tag_pk = None
            tag_slug = None
            if self.tag:
                if isinstance(self.tag, six.integer_types):
                    tag_pk = self.tag
                elif isinstance(self.tag, six.string_types):
                    tag_slug = self.tag
            else:
                tag_pk = self.kwargs.get('tag_pk')
                tag_slug = self.kwargs.get('tag_slug')
                if (not tag_pk
                        and not tag_slug
                        and (self, 'allow_get_parameters', False)):
                    tag_slug = (self.request.GET.get('tag')
                                or self.request.GET.get('t'))

            try:
                if tag_pk:
                    tag = TagManager.get(pk=tag_pk)
                elif tag_slug:
                    tag = TagManager.get(slug=tag_slug)
            except Tag.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': Tag._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if tag is None and self.require_tag:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': Tag._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._tag = tag

        return self._tag

    def get_context_data(self, **kwargs):
        context = super(TagMixin, self).get_context_data(**kwargs)
        context['tag'] = self.get_tag()
        return context

    def get_queryset(self):
        qs = super(TagMixin, self).get_queryset()
        if self.get_tag():
            qs = qs.filter(**{self.tag_field: self.get_tag()})
        return qs

