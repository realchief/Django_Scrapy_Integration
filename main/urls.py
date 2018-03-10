from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^upload/$', views.Upload, name='upload'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^api/crawl/', views.crawl, name='crawl'),
]