"""LBPMdashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include
#from django.conf.urls import include, url
from django.conf import settings
#from django.urls import re_path
#from django.views.static import serve
from django.conf.urls.static import static

urlpatterns = [
    path('project/', include('upload.urls')),
    path('LBPM/', include('LBPM.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    #re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
    #path('media/','django.views.static.serve','media'),
    #url(r'^media/$',media,name='media'),
 ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

