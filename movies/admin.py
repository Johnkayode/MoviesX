from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Movie)
admin.site.register(Screenshot)

class MovieInline(admin.TabularInline):
    model = Movie.genres.through
    extra=3

 

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):

    inlines = (MovieInline,) 
    
