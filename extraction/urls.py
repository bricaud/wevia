from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
	#url(r'^outputs/', views.request_output_page, name='outputs'),
]