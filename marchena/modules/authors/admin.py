# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import admin
from yepes.apps import apps

from marchena.admin import BlogModelAdmin

Author = apps.get_model('authors', 'Author')


class AuthorMixin(object):

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

class AuthorAdmin(AuthorMixin, BlogModelAdmin):
    pass


admin.site.register(Author, AuthorAdmin)
