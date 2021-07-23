from django.urls import path
from django.conf.urls import url, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
	path('typo/', views.typo),
	path('typoptions/', views.typoptions),
	path('types/', views.types),
	path('scheme/', views.changeScheme),
	url(r'^api-auth/', include('rest_framework.urls'))
]
