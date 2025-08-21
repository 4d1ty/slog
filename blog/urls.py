from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.post_list, name="post_list"),
    path("posts/public/", views.public_post_list, name="public_post_list"),
    path("posts/create/", views.create_post, name="create_post"),
    path("posts/<slug:slug>/", views.post_detail, name="post_detail"),
    path("posts/<slug:slug>/edit/", views.edit_post, name="edit_post"),
    path("posts/<slug:slug>/delete/", views.delete_post, name="delete_post"),
    path("posts/<int:post_id>/react/", views.post_react, name="post_react"),
]