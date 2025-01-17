from django.urls import path
from .views import UserRegestration, user_login, profile, EditProfileView, CustomLogoutView, user_profile, create_post
from django.contrib.auth.views import LogoutView

from django.conf import settings
from django.conf.urls.static import static


app_name = 'users'
urlpatterns = [
    path('regestration/', UserRegestration.as_view(), name='regestration'),
    path('login/', user_login, name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', user_profile, name='user_profile'),
    path('profile/<str:username>', profile, name='profile'),
    path('edit/', EditProfileView.as_view(), name='edit_profile'),
    path('post/', create_post, name='create_post'),
]
