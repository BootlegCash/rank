from django.urls import path
from . import views
from .views import CreatePostView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('welcome/', views.welcome, name='welcome'),
    path('profile/', views.profile, name='profile'),
    path('update_stats/', views.update_stats, name='update_stats'),
    path('send_friend_request/', views.send_friend_request, name='send_friend_request'),
    path('friend_list/', views.friend_list, name='friend_list'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),    
    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('compose/', CreatePostView.as_view(), name='create_post'),
]