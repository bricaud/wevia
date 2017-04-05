from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^dbinfo/(?P<document_query>[-\ .\w]+)$', views.dbinfo, name='dbinfo'),
	url(r'^dbinfomod/(?P<document_query>[-\ .\w]+)$', views.dbinfo_and_modif, name='dbinfomod'),
	url(r'^dbmodif/$', views.modif_db, name='dbmodif'),
]