from django.conf.urls import url

from . import views

urlpatterns = [
	#url(r'^$', views.index, name='index'),
	url(r'^$', views.request_page, name='test1'),
	url(r'^outputs/', views.request_output_page, name='outputs'),
	url(r'^results/', views.request_display_csv, name='results'),
	url(r'^searchresults/', views.request_search_results, name='search_results'),
]
