# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from functools import update_wrapper

from django.conf.urls import url
from django.utils.http import urlencode

from yepes import admin
from yepes.loading import LazyModel

Blog = LazyModel('blogs', 'Blog')


class BlogModelAdmin(admin.ModelAdmin):

    blog_field = 'blog'

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(BlogModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'blog':
            user = kwargs['request'].user
            blogs = Blog.objects.filter(authors=user)
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

    def get_preserved_filters(self, request):
        match = request.resolver_match
        if self.preserve_filters and match:
            current_url = '{0}:{1}'.format(match.app_name, match.url_name)
            changelist_url = '{0}:{1}_{2}_changelist'.format(
                    self.admin_site.name,
                    self.opts.app_label,
                    self.opts.model_name)
            if current_url == changelist_url:
                preserved_filters = request.GET.urlencode()
            else:
                preserved_filters = request.GET.get('_changelist_filters')

            if preserved_filters:
                return urlencode({'_changelist_filters': preserved_filters})

        return ''

    def get_queryset(self, request):
        qs = super(BlogModelAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(**{'{0}__authors'.format(self.blog_field): request.user})
        return qs

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = (self.model._meta.app_label, self.model._meta.model_name)

        urlpatterns = [
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
        ]
        return urlpatterns

