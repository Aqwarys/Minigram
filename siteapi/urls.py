from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter

routers = DefaultRouter()
routers.register('profiles', views.ProfileListView)

app_name = "api"
urlpatterns = [
    path('hello/', views.hello_world_view, name='hello'),
    path('communities/', views.CommunitiesListView.as_view(), name='communities_api'),
    path('profiles/', include(routers.urls))
]
