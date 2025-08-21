from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.game_upload, name="game_upload"),
    path("list/", views.game_list, name="game_list"),
    path("play/<slug:slug>/", views.game_play, name="game_play"),
    path("edit/<slug:slug>/", views.game_edit, name="game_edit"),
    path("delete/<slug:slug>/", views.game_delete, name="game_delete"),
]