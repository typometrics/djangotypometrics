from django.urls import path
from django.conf.urls import url, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
	path('draft/', views.dddraft),
	url(r'^api-auth/', include('rest_framework.urls'))
]