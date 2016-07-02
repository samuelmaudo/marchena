# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from copy import deepcopy
from functools import update_wrapper

from django.conf.urls import patterns, url, include
from django.contrib.admin.utils import quote
from django.contrib.admin.views.main import ChangeList
from django.contrib.contenttypes import views as contenttype_views
from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils import six
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache

from yepes import admin
from yepes.apps import apps
from yepes.conf import settings

from marchena.admin import BlogModelAdmin

AuthorMixin = apps.get_class('authors.admin', 'AuthorMixin')
CategoryMixin = apps.get_class('posts.admin', 'CategoryMixin')
CommentMixin = apps.get_class('comments.admin', 'CommentMixin')
LinkMixin = apps.get_class('links.admin', 'LinkMixin')
LinkCategoryMixin = apps.get_class('links.admin', 'LinkCategoryMixin')
PostMixin = apps.get_class('posts.admin', 'PostMixin')
TagMixin = apps.get_class('posts.admin', 'TagMixin')

Author = apps.get_model('authors', 'Author')
Blog = apps.get_model('blogs', 'Blog')
BlogManager = Blog._default_manager
Category = apps.get_model('posts', 'Category')
Comment = apps.get_model('comments', 'Comment')
Link = apps.get_model('links', 'Link')
LinkCategory = apps.get_model('links', 'LinkCategory')
Post = apps.get_model('posts', 'Post')
Tag = apps.get_model('posts', 'Tag')


class DeskSite(admin.AdminSite):

    def __init__(self, name='desk', app_name='desk'):
        super(DeskSite, self).__init__(name, app_name)

    def app_index(self, request, app_label, extra_context=None):
        user = request.user
        blogs = BlogManager
        if not user.is_superuser:
            blogs = blogs.filter(authors=user)

        try:
            blog = blogs.get(slug=app_label)
        except Blog.DoesNotExit:
            raise Http404('The requested admin page does not exist.')

        app_dict = {}
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label)
            if not has_module_perms:
                continue

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            perms = model_admin.get_model_perms(request)
            if True not in perms.values():
                continue

            info = (self.name, app_label, model._meta.module_name)
            kwargs = {'blog_slug': blog.slug}
            model_dict = {
                'name': capfirst(model._meta.verbose_name_plural),
                'perms': perms,
            }
            if perms.get('change', False):
                try:
                    view_name = '{0}:{1}_{2}_changelist'.format(*info)
                    model_dict['admin_url'] = reverse(view_name, kwargs=kwargs)
                except NoReverseMatch:
                    pass
            if perms.get('add', False):
                try:
                    view_name = '{0}:{1}_{2}_add'.format(*info)
                    model_dict['add_url'] = reverse(view_name, kwargs=kwargs)
                except NoReverseMatch:
                    pass
            if app_dict:
                app_dict['models'].append(model_dict),
            else:
                # First time around, now that we know there's
                # something to display, add in the necessary meta
                # information.
                app_dict = {
                    'name': blog.title,
                    'app_url': '',
                    'has_module_perms': has_module_perms,
                    'models': [model_dict],
                }

        if not app_dict:
            raise Http404('The requested admin page does not exist.')

        # Sort the models alphabetically within each app.
        app_dict['models'].sort(key=lambda x: x['name'])

        context = {
            'title': _("{0}'s desk").format(blog.title),
            'app_list': [app_dict],
        }
        context.update(extra_context or {})
        return TemplateResponse(request, self.app_index_template or [
            'desk/app_index.html',
            'admin/app_index.html',
        ], context, current_app=self.name)

    def get_model_urls(self):
        """
        Model's views.
        """
        urlpatterns = []
        for model, model_admin in six.iteritems(self._registry):
            urlpatterns += patterns('',
                url(r'^(?P<blog_slug>[a-z\-]+)/{0}/'.format(
                                    model._meta.module_name),
                    include(model_admin.urls)),
            )
        return urlpatterns

    def get_site_urls(self):
        """
        Admin-site-wide views.
        """
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        return patterns('',
            url(r'^$',
                wrap(self.index),
                name='index'),
            url(r'^logout/$',
                wrap(self.logout),
                name='logout'),
            url(r'^password_change/$',
                wrap(self.password_change, cacheable=True),
                name='password_change'),
            url(r'^password_change/done/$',
                wrap(self.password_change_done, cacheable=True),
                name='password_change_done'),
            url(r'^jsi18n/$',
                wrap(self.i18n_javascript, cacheable=True),
                name='jsi18n'),
            url(r'^r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$',
                wrap(contenttype_views.shortcut),
                name='view_on_site'),
            url(r'^(?P<app_label>[a-z\-]+)/$',
                wrap(self.app_index),
                name='app_list'))

    def get_urls(self):
        if settings.DEBUG:
            self.check_dependencies()
        urlpatterns = self.get_site_urls()
        urlpatterns.extend(self.get_model_urls())
        return urlpatterns

    @never_cache
    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        user = request.user
        blogs = BlogManager.get_queryset()
        if not user.is_superuser:
            blogs = blogs.filter(authors=user)

        app_dict = {}
        for blog in blogs:
            for model, model_admin in six.iteritems(self._registry):
                app_label = model._meta.app_label
                has_module_perms = user.has_module_perms(app_label)
                if not has_module_perms:
                    continue

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                perms = model_admin.get_model_perms(request)
                if True not in perms.values():
                    continue

                info = (self.name, app_label, model._meta.module_name)
                kwargs = {'blog_slug': blog.slug}
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'perms': perms,
                }
                if perms.get('change', False):
                    try:
                        view_name = '{0}:{1}_{2}_changelist'.format(*info)
                        model_dict['admin_url'] = reverse(view_name, kwargs=kwargs)
                    except NoReverseMatch:
                        pass
                if perms.get('add', False):
                    try:
                        view_name = '{0}:{1}_{2}_add'.format(*info)
                        model_dict['add_url'] = reverse(view_name, kwargs=kwargs)
                    except NoReverseMatch:
                        pass
                if blog.slug in app_dict:
                    app_dict[blog.slug]['models'].append(model_dict)
                else:
                    app_dict[blog.slug] = {
                        'name': blog.title,
                        'app_url': reverse('{0}:app_list'.format(self.name),
                                           kwargs={'app_label': blog.slug}),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }

        # Sort the apps alphabetically.
        app_list = list(six.itervalues(app_dict))
        app_list.sort(key=lambda x: x['name'])

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        context = {
            'title': _('Desk'),
            'app_list': app_list,
        }
        context.update(extra_context or {})
        return TemplateResponse(request, self.index_template or [
            'desk/index.html',
            'admin/index.html',
        ], context, current_app=self.name)

desk_site = DeskSite()


class DeskChangeList(ChangeList):

    def __init__(self, request, *args, **kwargs):
        self.blog = request.blog
        super(DeskChangeList, self).__init__(request, *args, **kwargs)

    def url_for_result(self, result):
        view_name = '{0}:{1}_{2}_change'.format(
                self.model_admin.admin_site.name,
                self.opts.app_label,
                self.opts.module_name)
        kwargs = {'object_id': quote(getattr(result, self.pk_attname))}
        kwargs['blog_slug'] = quote(self.blog.slug)
        return reverse(view_name, kwargs=kwargs)


class BlogModelDesk(BlogModelAdmin):

    change_form_template = 'desk/change_form.html'
    change_list_template = 'desk/change_list.html'
    delete_confirmation_template = 'desk/delete_confirmation.html'
    object_history_template = 'desk/object_history.html'

    def add_view(self, request, form_url='', extra_context=None, blog_slug=None):
        request.blog = BlogManager.get(slug=blog_slug)
        context = {'app_label': request.blog.title}
        context.update(extra_context or {})
        return super(BlogModelDesk, self).add_view(request, form_url, context)

    def change_view(self, request, object_id, form_url='', extra_context=None, blog_slug=None):
        request.blog = BlogManager.get(slug=blog_slug)
        context = {'app_label': request.blog.title}
        context.update(extra_context or {})
        return super(BlogModelDesk, self).change_view(request, object_id, form_url, context)

    def changelist_view(self, request, extra_context=None, blog_slug=None):
        request.blog = BlogManager.get(slug=blog_slug)
        context = {'app_label': request.blog.title}
        context.update(extra_context or {})
        return super(BlogModelDesk, self).changelist_view(request, context)

    def delete_view(self, request, object_id, extra_context=None, blog_slug=None):
        request.blog = BlogManager.get(slug=blog_slug)
        context = {'app_label': request.blog.title}
        context.update(extra_context or {})

        # This sucks but is the best solution that I have found.
        original_registry = self.admin_site._registry
        self.admin_site._registry = {}
        response = super(BlogModelDesk, self).delete_view(request, object_id, context)
        self.admin_site._registry = original_registry

        return response

    def get_changelist(self, request, **kwargs):
        return DeskChangeList

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(BlogModelDesk, self).get_fieldsets(request, obj)
        fs = []
        for title, opts in deepcopy(fieldsets):
            fields = opts.get('fields', ())
            try:
                i = fields.index('blog')
            except ValueError:
                pass
            else:
                if len(fields) == 1:
                    continue
                fields = list(fields)
                fields.pop(i)
                opts['fields'] = fields

            fs.append((title, opts))

        return fs

    def get_queryset(self, request):
        qs = super(BlogModelAdmin, self).get_queryset(request)
        qs = qs.filter(**{self.blog_field: request.blog})
        return qs

    def history_view(self, request, object_id, extra_context=None, blog_slug=None):
        request.blog = BlogManager.get(slug=blog_slug)
        context = {'app_label': request.blog.title}
        context.update(extra_context or {})
        return super(BlogModelDesk, self).history_view(request, object_id, context)

    def save_model(self, request, obj, *args, **kwargs):
        if hasattr(request, 'blog') and '__' not in self.blog_field:
            setattr(obj, self.blog_field, request.blog)
        super(BlogModelDesk, self).save_model(request, obj, *args, **kwargs)


class AuthorDesk(AuthorMixin, BlogModelDesk):
    pass


class CategoryDesk(CategoryMixin, BlogModelDesk):
    pass


class CommentDesk(CommentMixin, BlogModelDesk):
    pass


class LinkDesk(LinkMixin, BlogModelDesk):
    pass


class LinkCategoryDesk(LinkCategoryMixin, BlogModelDesk):
    pass


class PostDesk(PostMixin, admin.DisplayableMixin, BlogModelDesk):
    pass


class TagDesk(TagMixin, BlogModelDesk):
    pass


desk_site.register(Author, AuthorDesk)
desk_site.register(Category, CategoryDesk)
desk_site.register(Comment, CommentDesk)
desk_site.register(Link, LinkDesk)
desk_site.register(LinkCategory, LinkCategoryDesk)
desk_site.register(Post, PostDesk)
desk_site.register(Tag, TagDesk)

