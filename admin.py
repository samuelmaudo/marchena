# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from copy import deepcopy
from functools import update_wrapper

from django import forms
from django.conf.urls import patterns, url, include
from django.contrib.admin.util import quote
from django.contrib.admin.views.main import ChangeList
from django.contrib.contenttypes import views as contenttype_views
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.db.models import Count
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils import six, timezone
from django.utils.formats import date_format
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.six.moves.urllib.parse import urljoin
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache

from yepes import admin
from yepes.conf import settings
from yepes.loading import get_model
from yepes.utils.humanize import naturalday

Author = get_model('marchena', 'Author')
Blog = get_model('marchena', 'Blog')
Category = get_model('marchena', 'Category')
Comment = get_model('marchena', 'Comment')
CommentStatus = get_model('marchena', 'CommentStatus')
Link = get_model('marchena', 'Link')
LinkCategory = get_model('marchena', 'LinkCategory')
Post = get_model('marchena', 'Post')
PostImage = get_model('marchena', 'PostImage')
Tag = get_model('marchena', 'Tag')


class BlogAdminSite(admin.AdminSite):

    def __init__(self, name='desk', app_name='desk'):
        super(BlogAdminSite, self).__init__(name, app_name)

    def app_index(self, request, app_label, extra_context=None):
        user = request.user
        blogs = Blog._default_manager
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
        blogs = Blog._default_manager.get_queryset()
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

blog_admin_site = BlogAdminSite()


class BlogChangeList(ChangeList):

    def __init__(self, request, *args, **kwargs):
        self.blog = getattr(request, 'blog', None)
        super(BlogChangeList, self).__init__(request, *args, **kwargs)

    def url_for_result(self, result):
        view_name = '{0}:{1}_{2}_change'.format(
                self.model_admin.admin_site.name,
                self.opts.app_label,
                self.opts.module_name)
        kwargs = {'object_id': quote(getattr(result, self.pk_attname))}
        if self.blog is not None:
            kwargs['blog_slug'] = quote(self.blog.slug)

        return reverse(view_name, kwargs=kwargs)


class BlogModelAdmin(admin.ModelAdmin):

    blog_field = 'blog'

    def add_view(self, request, form_url='', extra_context=None, blog_slug=None):
        if blog_slug is not None:
            request.blog = Blog._default_manager.get(slug=blog_slug)
            context = {'app_label': request.blog.title}
            context.update(extra_context or {})
        else:
            context = extra_context
        return super(BlogModelAdmin, self).add_view(request, form_url, context)

    def change_view(self, request, object_id, form_url='', extra_context=None, blog_slug=None):
        if blog_slug is not None:
            request.blog = Blog._default_manager.get(slug=blog_slug)
            context = {'app_label': request.blog.title}
            context.update(extra_context or {})
        else:
            context = extra_context
        return super(BlogModelAdmin, self).change_view(request, object_id, form_url, context)

    def changelist_view(self, request, extra_context=None, blog_slug=None):
        if blog_slug is not None:
            request.blog = Blog._default_manager.get(slug=blog_slug)
            context = {'app_label': request.blog.title}
            context.update(extra_context or {})
        else:
            context = extra_context
        return super(BlogModelAdmin, self).changelist_view(request, context)

    def delete_view(self, request, object_id, extra_context=None, blog_slug=None):
        if blog_slug is None:
            return super(BlogModelAdmin, self).delete_view(request, object_id, extra_context)

        request.blog = Blog._default_manager.get(slug=blog_slug)
        context = {'app_label': request.blog.title}
        context.update(extra_context or {})

        # This sucks but is the best solution that I have found.
        original_registry = self.admin_site._registry
        self.admin_site._registry = {}
        response = super(BlogModelAdmin, self).delete_view(request, object_id, context)
        self.admin_site._registry = original_registry

        return response

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(BlogModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'blog':
            user = kwargs['request'].user
            blogs = Blog._default_manager.filter(authors=user)
            try:
                formfield.initial = blogs[0]
            except IndexError:
                pass
        return formfield

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        formfield = super(BlogModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        #if hasattr(request, 'blog'):
            #formfield.rel =
        return formfield

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        formfield = super(BlogModelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
        #if hasattr(request, 'blog'):
            #formfield.rel =
        return formfield

    def get_change_form_template(self, request):
        if not hasattr(request, 'blog'):
            return super(BlogModelAdmin, self).get_change_form_template(request)

        if self.change_form_template is not None:
            template = self.change_form_template
        else:
            model = self.model._meta
            template = [
                'desk/{0}/change_form.html'.format(model.object_name.lower()),
                'desk/change_form.html',
                'admin/change_form.html',
            ]
        return template

    def get_change_list_template(self, request):
        if not hasattr(request, 'blog'):
            return super(BlogModelAdmin, self).get_change_list_template(request)

        if self.change_list_template is not None:
            template = self.change_list_template
        else:
            model = self.model._meta
            template = [
                'desk/{0}/change_list.html'.format(model.object_name.lower()),
                'desk/change_list.html',
                'admin/change_list.html',
            ]
        return template

    def get_changelist(self, request, **kwargs):
        return BlogChangeList

    def get_delete_confirmation_template(self, request):
        if not hasattr(request, 'blog'):
            return super(BlogModelAdmin, self).get_delete_confirmation_template(request)

        if self.delete_confirmation_template is not None:
            template = self.delete_confirmation_template
        else:
            model = self.model._meta
            template = [
                'desk/{0}/delete_confirmation.html'.format(model.object_name.lower()),
                'desk/delete_confirmation.html',
                'admin/delete_confirmation.html',
            ]
        return template

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(BlogModelAdmin, self).get_fieldsets(request, obj)
        if not hasattr(request, 'blog'):
            return fieldsets

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

    def get_object_history_template(self, request):
        if not hasattr(request, 'blog'):
            return super(BlogModelAdmin, self).get_object_history_template(request)

        if self.object_history_template is not None:
            template = self.object_history_template
        else:
            model = self.model._meta
            template = [
                'desk/{0}/object_history.html'.format(model.object_name.lower()),
                'desk/object_history.html',
                'admin/object_history.html',
            ]
        return template

    def get_preserved_filters(self, request):
        match = request.resolver_match
        if self.preserve_filters and match:
            current_url = '{0}:{1}'.format(match.app_name, match.url_name)
            changelist_url = '{0}:{1}_{2}_changelist'.format(
                    self.admin_site.name,
                    self.opts.app_label,
                    self.opts.module_name)
            if current_url == changelist_url:
                preserved_filters = request.GET.urlencode()
            else:
                preserved_filters = request.GET.get('_changelist_filters')

            if preserved_filters:
                return urlencode({'_changelist_filters': preserved_filters})

        return ''

    def get_queryset(self, request):
        qs = super(BlogModelAdmin, self).queryset(request)
        if hasattr(request, 'blog'):
            qs = qs.filter(**{self.blog_field: request.blog})
        elif not request.user.is_superuser:
            qs = qs.filter(**{'{0}__authors'.format(self.blog_field): request.user})
        return qs

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = (self.model._meta.app_label, self.model._meta.module_name)

        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.changelist_view),
                name='{0}_{1}_changelist'.format(*info),
            ),
            url(r'^add/$',
                wrap(self.add_view),
                name='{0}_{1}_add'.format(*info),
            ),
            url(r'^(?P<object_id>.+)/history/$',
                wrap(self.history_view),
                name='{0}_{1}_history'.format(*info),
            ),
            url(r'^(?P<object_id>.+)/delete/$',
                wrap(self.delete_view),
                name='{0}_{1}_delete'.format(*info),
            ),
            url(r'^(?P<object_id>.+)/$',
                wrap(self.change_view),
                name='{0}_{1}_change'.format(*info),
            ),
        )
        return urlpatterns

    def history_view(self, request, object_id, extra_context=None, blog_slug=None):
        if blog_slug is not None:
            request.blog = Blog._default_manager.get(slug=blog_slug)
            context = {'app_label': request.blog.title}
            context.update(extra_context or {})
        else:
            context = extra_context
        return super(BlogModelAdmin, self).history_view(request, object_id, context)

    def save_model(self, request, obj, *args, **kwargs):
        if hasattr(request, 'blog'):
            setattr(obj, self.blog_field, request.blog)
        super(BlogModelAdmin, self).save_model(request, obj, *args, **kwargs)


class AuthorAdmin(BlogModelAdmin):

    blog_field = 'blogs'
    fieldsets = [
        (None, {
            'fields': [
                'first_name',
                'last_name',
                'admin_username',
                'email',
            ],
        }),
    ]
    list_display = ['admin_full_name', 'admin_username', 'email']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    ordering = ['first_name', 'last_name']
    readonly_fields = ['admin_username']
    search_fields = ['username', 'first_name', 'last_name', 'email']

    def admin_full_name(self, obj):
        return obj.get_full_name()
    admin_full_name.admin_order_field = 'first_name'
    admin_full_name.short_description = _('Full name')

    def admin_username(self, obj):
        return obj.username
    admin_username.admin_order_field = 'username'
    admin_username.short_description = _('Username')

    def _has_add_permission(self, request):
        return False

    def _has_change_permission(self, request, obj):
        return (request.user.is_superuser or request.user.pk == obj.pk)

    def _has_view_permission(self, request, obj):
        return True


class BlogAdmin(admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  [],
        'm2m': ['authors'],
    }
    fieldsets = [
        (None, {
            'fields': [
                'title',
                'subtitle',
                'description',
                'authors'
            ],
        }),
        (_('Metadata'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'meta_title',
                'slug',
                'meta_description',
                'meta_keywords',
            ]
        }),
        (_('Image'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'image',
            ],
        }),
    ]
    list_display = ['title', 'subtitle', 'admin_authors']
    prepopulated_fields = {'slug': ('title', )}
    raw_id_fields = ['authors']
    search_fields = ['title', 'subtitle']

    def admin_authors(self, obj):
        links = [
            format_html('<a href="?authors__id__exact={0}">{1}</a>',
                        user.pk,
                        user.get_full_name() or user.get_username())
            for user
            in obj.authors.all()
        ]
        return ', '.join(links) if links else _('No authors')
    admin_authors.allow_tags = True
    admin_authors.short_description = _('Authors')

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(BlogAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'authors':
            formfield.initial = [kwargs['request'].user]
        return formfield

    def get_queryset(self, request):
        qs = super(BlogAdmin, self).queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(authors=request.user)
        return qs


class CategoryAdmin(BlogModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  ['blog'],
        'm2m': [],
    }
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'description',
            ],
        }),
        (_('Blog'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'blog',
            ]
        }),
        (_('Image'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'image',
            ],
        }),
        (_('Metadata'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'meta_title',
                'slug',
                'meta_description',
                'meta_keywords',
            ]
        }),
    ]
    list_display = ['name', 'description', 'slug', 'admin_post_count']
    prepopulated_fields = {'slug': ('name', )}
    raw_id_fields = ['blog']
    search_fields = ['name']

    def admin_post_count(self, obj):
        return obj.post_count
    admin_post_count.admin_order_field = 'post_count'
    admin_post_count.short_description = _('Posts')

    def get_queryset(self, request):
        qs = super(CategoryAdmin, self).queryset(request)
        qs = qs.annotate(post_count=Count('posts'))
        if not request.user.is_superuser:
            qs = qs.filter(blog__authors=request.user)
        return qs


class CommentAdmin(admin.ModelAdmin):

    date_hierarchy = 'creation_date'
    fieldsets = [
        (None, {
            'fields': [
                'content',
            ],
        }),
        (_('Author'), {
            'classes': [
                'grp-collapse',
                'grp-open',
            ],
            'fields': [
                'get_author_name',
                'get_author_email',
                'get_author_url',
            ]
        }),
        (_('Status'), {
            'classes': [
                'grp-collapse',
                'grp-open',
            ],
            'fields': [
                'status',
            ],
        }),
    ]
    list_display = [
        'admin_author',
        'admin_content',
        'admin_post',
    ]
    list_filter = ['status']
    list_select_related = True
    ordering = ['-creation_date']
    readonly_fields = [
        'get_author_email',
        'get_author_name',
        'get_author_url',
    ]
    search_fields = ['content']

    def admin_author(self, obj):
        if obj.author_id is None:
            name = obj.get_author_name()
        else:
            name = format_html(
                '{0} <img src="{1}" alt="({2})">',
                obj.get_author_name(),
                urljoin(settings.STATIC_URL, 'admin/img/icon-yes.gif'),
                _('Authenticated'))
        url = obj.get_author_url()
        return format_html('{0}<br><a href="{1}">{1}</a>', name, url)
    admin_author.allow_tags = True
    admin_author.short_description = _('Author')

    def admin_content(self, obj):
        status = obj.get_status()
        color = '#42AD3F' if status.publish_comment else '#DE2121'
        return format_html(
            '{0}: <span style="color:{1}">{2}</span><br>{3}',
            _('Status'),
            color,
            status,
            obj.get_excerpt())
    admin_content.allow_tags = True
    admin_content.short_description = _('Content')

    def admin_post(self, obj):
        return format_html(
            '{0}<br><a href="{1}">{2}</a>',
            obj.post,
            obj.get_absolute_url(),
            _('View Post'))
    admin_content.allow_tags = True
    admin_content.short_description = _('Post')

    def _has_add_permission(self, request):
        return False


class CommentStatusAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                ('label', 'publish_comment'),
                'api_id',
                'comment_replacement',
            ],
        }),
    ]
    list_display = ['label', 'api_id', 'admin_comment_count', 'index']
    list_editable = ['index']
    search_fields = ['label', 'api_id']

    def admin_comment_count(self, obj):
        return obj.comment_count
    admin_comment_count.admin_order_field = 'comment_count'
    admin_comment_count.short_description = _('Comments')

    def get_queryset(self, request):
        qs = super(CommentStatusAdmin, self).queryset(request)
        qs = qs.annotate(comment_count=Count('comments'))
        return qs


class LinkAdmin(BlogModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  ['blog', 'category'],
        'm2m': [],
    }
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'url',
                'description',
                'category',
            ],
        }),
        (_('Blog'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'blog',
            ]
        }),
        (_('Image'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'image',
            ],
        }),
    ]
    list_display = ['name', 'url', 'category']
    list_filter = ['blog', 'category']
    list_select_related = True
    raw_id_fields = ['blog', 'category']
    search_fields = ['name', 'url']

    def get_queryset(self, request):
        qs = super(LinkAdmin, self).queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(blog__authors=request.user)
        return qs


class LinkCategoryAdmin(BlogModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  ['blog'],
        'm2m': [],
    }
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'description',
            ],
        }),
        (_('Blog'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'blog',
            ]
        }),
        (_('Metadata'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'slug',
            ]
        }),
    ]
    list_display = ['name', 'description', 'slug', 'admin_link_count']
    prepopulated_fields = {'slug': ('name', )}
    raw_id_fields = ['blog']
    search_fields = ['name']

    def admin_link_count(self, obj):
        return obj.link_count
    admin_link_count.admin_order_field = 'link_count'
    admin_link_count.short_description = _('Links')

    def get_queryset(self, request):
        qs = super(LinkCategoryAdmin, self).queryset(request)
        qs = qs.annotate(link_count=Count('links'))
        if not request.user.is_superuser:
            qs = qs.filter(blog__authors=request.user)
        return qs


class PostImageInline(admin.TabularInline):

    classes = ['grp-collapse', 'grp-closed']
    formfield_overrides = {
        models.PositiveIntegerField: {
            'widget': forms.HiddenInput
        },
    }
    extra = 0
    model = PostImage
    sortable_field_name = 'index'


class PostAdmin(admin.DisplayableMixin, BlogModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  ['blog'],
        'm2m': ['authors', 'categories', 'tags'],
    }
    date_hierarchy = 'creation_date'
    fieldsets = [
        (None, {
            'fields': [
                'title',
                'subtitle',
                'content',
                'authors',
                'categories',
                'tags',
            ],
        }),
        (_('Blog'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'blog',
            ]
        }),
        (_('Metadata'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'meta_title',
                'slug',
                'meta_description',
                'meta_keywords',
            ]
        }),
        (_('Visibility'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'publish_status',
                'publish_from',
                'publish_to',
            ]
        }),
        (_('Excerpt'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'excerpt',
            ]
        }),
        (_('Discussion'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'comment_status',
                'ping_status',
            ]
        }),
    ]
    inlines = [PostImageInline]
    list_display = [
        'title',
        'admin_authors',
        'admin_categories',
        'admin_tags',
        'comment_count',
        'admin_date',
    ]
    list_filter = [
        'authors',
        'blog',
        'categories',
        'tags',
        'publish_status',
    ]
    list_select_related = True
    prepopulated_fields = {'slug': ('title', )}
    raw_id_fields = ['authors', 'blog', 'categories', 'tags']
    search_fields = ['title', 'content']

    def admin_authors(self, obj):
        links = [
            format_html('<a href="?authors__id__exact={0}">{1}</a>',
                        author.pk,
                        author)
            for author
            in obj.authors.all()
        ]
        return ', '.join(links) if links else _('No author')
    admin_authors.allow_tags = True
    admin_authors.short_description = _('Authors')

    def admin_categories(self, obj):
        links = [
            format_html('<a href="?categories__id__exact={0}">{1}</a>',
                        category.pk,
                        category)
            for category
            in obj.categories.all()
        ]
        return ', '.join(links) if links else _('No category')
    admin_categories.allow_tags = True
    admin_categories.short_description = _('Categories')

    def admin_date(self, obj):
        if obj.is_draft():
            status = _('Draft')
        elif obj.is_hidden():
            status = _('Hidden')
        elif obj.is_published():
            status = _('Published')
        elif (obj.publish_from is not None
                and obj.publish_from >= timezone.now()):
            status = _('Future post')
        else:
            status = _('Expired post')
        return format_html(
            '<abbr title="{0}">{1}</abbr><br>{2}',
            date_format(obj.publish_from, 'DATETIME_FORMAT'),
            naturalday(obj.publish_from),
            status)
    admin_date.admin_order_field = 'publish_from'
    admin_date.allow_tags = True
    admin_date.short_description = _('Date')

    def admin_tags(self, obj):
        links = [
            format_html('<a href="?tags__id__exact={0}">{1}</a>', tag.pk, tag)
            for tag
            in obj.tags.all()
        ]
        return ', '.join(links) if links else _('No tag')
    admin_tags.allow_tags = True
    admin_tags.short_description = _('Tags')

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'authors':
            formfield.initial = [kwargs['request'].user]
        return formfield

    def get_queryset(self, request):
        qs = super(PostAdmin, self).queryset(request)
        qs = qs.prefetch_related('authors', 'categories', 'tags')
        return qs


class TagAdmin(BlogModelAdmin):

    blog_field = 'posts__blog'
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'description',
            ],
        }),
        (_('Metadata'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'slug',
            ]
        }),
    ]
    list_display = ['name', 'description', 'slug', 'admin_post_count']
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ['name']

    def admin_post_count(self, obj):
        return obj.post_count
    admin_post_count.admin_order_field = 'post_count'
    admin_post_count.short_description = _('Posts')

    def get_queryset(self, request):
        qs = super(TagAdmin, self).queryset(request)
        qs = qs.annotate(post_count=Count('posts'))
        if not request.user.is_superuser:
            qs = qs.filter(blog__authors=request.user)
        return qs


admin.site.register(Author, AuthorAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentStatus, CommentStatusAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(LinkCategory, LinkCategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)

blog_admin_site.register(Author, AuthorAdmin)
blog_admin_site.register(Category, CategoryAdmin)
blog_admin_site.register(Link, LinkAdmin)
blog_admin_site.register(LinkCategory, LinkCategoryAdmin)
blog_admin_site.register(Post, PostAdmin)
blog_admin_site.register(Tag, TagAdmin)

