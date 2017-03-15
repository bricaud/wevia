from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
	url(r'^outputs/', views.request_output_page, name='outputs'),
	url(r'^results/', views.request_display_csv, name='classif_results'),	
]