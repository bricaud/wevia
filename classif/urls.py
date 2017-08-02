from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
	url(r'^outputs/', views.request_output_page, name='outputs'),
	url(r'^results/', views.request_display_classif, name='classif_results'),
	url(r'^groupsOfFiles/', views.request_groups_of_files, name='groups_of_files'),
	url(r'^dbinfo/(?P<cluster_query>[-\ .\w]+)$', views.dbinfo, name='dbinfo'),
]