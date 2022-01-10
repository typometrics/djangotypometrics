from django.urls import path
from django.conf.urls import include #url has been removed from django4.0
from . import views

urlpatterns = [
    path('', views.index, name='index'),
	path('typo/', views.typo),
	path('typoptions/', views.typoptions),
	path('types/', views.types),
	path('scheme/', views.changeScheme),
	path('graph/',views.getCloseGraph),
	path('graphParam/', views.getGraphParam),
	path('api-auth/', include('rest_framework.urls'))
]
