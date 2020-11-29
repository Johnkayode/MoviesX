
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/<slug:slug>/', views.movie, name='movie'),
    path('genres/', views.genres, name='genres'),
    path('genres/<slug:slug>/', views.home, name='movie_by_genre'),
    path('search/', views.search, name='search')
]