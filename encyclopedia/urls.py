from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("_newpage", views.newPage, name="newPage"),
    path("_search", views.search, name="search"),
    path("<str:title>", views.display, name="display"),
]
