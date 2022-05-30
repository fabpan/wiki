from django.urls import path, register_converter, re_path
from . import views, converters


register_converter(converters.WikiEntryConverter, 'til')

urlpatterns = [
    path("", views.index, name="index"),
    path("_random", views.random, name="random"),
    path("_editpage", views.updatePage, {"action": "edit"}, name="editPage",),
    path("_newpage", views.updatePage, {"action": "newpage"}, name="newPage"),
    path("_search", views.search, name="search"),
    path("<til:title>", views.index, name="entrytitle"),
    path("<path:title>", views.handler404, name="handler404"),
]
