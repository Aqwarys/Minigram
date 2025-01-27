from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

from django.conf import settings
from django.conf.urls.static import static


app_name = 'users'
urlpatterns = [
    path('regestration/', views.UserRegestration.as_view(), name='regestration'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('post/', views.create_post, name='create_post'),
    path('post/<int:post_id>', views.view_post, name='post_view'),
    path('like/<int:post_id>', views.like, name='like'),
    path('bookmark/<int:post_id>', views.bookmark, name='bookmark'),
    path('follow/<int:user_pk>', views.follow, name='follow'),
    path('<str:username>/followers/', views.followers, name='followers'),
    path('<str:username>/following/', views.following, name='following'),
    path('<str:username>/friends', views.friends, name='friends'),
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
    path('community/<str:slugger>', views.community_view, name='community'),
    path('follow/<str:slugger>', views.community_follow, name='community_follow'),
]
