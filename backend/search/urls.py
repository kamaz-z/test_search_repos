from django.urls import path
from . import views

urlpatterns = [
    path("search/", views.SearchView.as_view(), name='search'),
    path("clear-cache/", views.ClearCacheView.as_view(), name='clear_cache'),
]