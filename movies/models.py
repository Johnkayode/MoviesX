from django.db import models
from django.urls import reverse

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=400, blank=True, null=True)
    slug = models.SlugField(max_length=1000, blank=True)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('movie_by_genre',args=[self.slug])


class Star(models.Model):
    name = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=1000, blank=True)
    year = models.PositiveIntegerField( blank=True, null=True)
    rating = models.CharField(max_length=5, blank=True, null=True)
    image_link = models.CharField(max_length=800, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    synopsis  = models.TextField(blank=True, null=True)
    director = models.CharField(max_length=250, blank=True, null=True)
    stars = models.ManyToManyField(Star)
    genres = models.ManyToManyField(Genre)
    imdb_link = models.CharField(max_length=800, blank=True, null=True)
    torrent_720p = models.CharField(max_length=800, blank=True, null=True)
    torrent_1080p = models.CharField(max_length=800, blank=True, null=True)


    def __str__(self):
        return self.title + ' ' + str(self.year)

    def get_absolute_url(self):
        return reverse('movie',args=[self.slug])







class Screenshot(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    link = models.CharField(max_length=800, blank=True, null=True)

    def __str__(self):
        return self.link