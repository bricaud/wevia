"""wevia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^commands/', include('commands.urls')),
	url(r'^admin/', admin.site.urls),
	url(r'^extraction/', include('extraction.urls')),
	url(r'^graphdesign/', include('graphdesign.urls')),
	url(r'^classif/', include('classif.urls')),
	url(r'^search/', include('search.urls')),
	url(r'^fileupload/', include('fileupload.urls')),
	url(r'^advancedsettings/', include('advancedSettings.urls')),
]
