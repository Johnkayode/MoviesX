from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count 
from .models import *
#from .scraper import all_movies



# Create your views here.


def home(request, slug=None):
    genre = None
    movies = Movie.objects.all().order_by('-year')
    if slug:
        genre = get_object_or_404(Genre, slug=slug)
        movies = genre.movie_set.all()
        genre = genre.name
    genres = Genre.objects.all()[:5]
    paginator = Paginator(movies, 21)
    page = request.GET.get('page')

    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)
    context = {'movies': movies, 'genres': genres, 'genre': genre}
    return render(request, 'home.html', context)

def search(request):
    genres = Genre.objects.all()[:5]
    queryset = Movie.objects.all()
    stars = Star.objects.all()
    q = request.GET.get('q')
    if q:
        movies = queryset.filter(
            Q(title__icontains=q) |
            Q(year__icontains=q)
        ).distinct()
        stars = stars.filter(Q(name__icontains=q))
        if stars:
            
            movies = queryset.filter(
            Q(title__icontains=q) |
            Q(year__icontains=q) |
            Q(stars__in=stars)
            ).distinct()
        
    paginator = Paginator(movies, 21)
    page = request.GET.get('page')

    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)
   

    context = {'movies':movies, 'q':q, 'genres':genres}

    return render(request, 'search.html', context)

def movie(request, slug):
    genres = Genre.objects.all()[:5]
    movie = get_object_or_404(Movie, slug=slug)
    context = {'movie':movie, 'genres':genres}
    return render(request, 'movie.html', context)

def genres(request):
    genres = Genre.objects.all()[:5]
    all_genres = Genre.objects.all()
    context = {'genres':genres, 'all_genres':all_genres}
    return render(request, 'genres.html', context)