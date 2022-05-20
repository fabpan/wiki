from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("_random", views.random, name="random"),
    path("_editpage", views.edit, name="editPage"),
    path("_newpage", views.newPage, name="newPage"),
    path("_search", views.search, name="search"),
    path("<str:title>", views.index, name="index"),
]
