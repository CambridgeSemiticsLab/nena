"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

import dialects.views

urlpatterns = [
    url(r'^$', dialects.views.homepage , name='index'),
    url(r'^about/$', dialects.views.about , name='about'),
    url(r'^contribute/$', dialects.views.contribute , name='contribute'),
    url(r'', include('ucamwebauth.urls')),
    url(r'^admin/login/$', RedirectView.as_view(pattern_name='raven_login', permanent=True, query_string=True)),
    url(r'^accounts/profile/$', RedirectView.as_view(pattern_name='index', permanent=True, query_string=True)),
    url(r'^accounts/non-raven$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
#    url(r'^accounts/logout$', auth_views., {'next_page': '/'}, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^dialects/', include(('dialects.urls'), namespace='dialects')),
    url(r'^dialectmaps/', include(('dialectmaps.urls'), namespace='dialectmaps')),
    url(r'^grammar/', include(('grammar.urls'), namespace='grammar')),
    url(r'^audio/', include(('audio.urls'), namespace='audio')),
    url(r'^gallery/', include(('gallery.urls'), namespace='gallery')),
    url('django-github-push-deploy/', include('django_github_push_deploy.urls')),
]

if not settings.GS_PROJECT_ID:  # if we're not using Google Storages to serve files, serve them locally
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
                              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
