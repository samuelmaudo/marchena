# -*- coding:utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from marchena.desk import desk_site

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^desk/', include(desk_site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^', include('marchena.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
