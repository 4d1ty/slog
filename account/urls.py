from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('github/login/', views.github_login, name='github_login'),
    path('github/login/callback/', views.github_callback, name='github_callback'),
    path('profile/', views.profile_view, name='profile'),
]