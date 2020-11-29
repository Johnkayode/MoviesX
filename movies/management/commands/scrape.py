import requests
import csv
import time
import re

from bs4 import BeautifulSoup
from time import sleep

from movies.models import *

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'collect jobs'

    def handle(self, *args, **options):

        print('Creating/Updating Movies...')

        URL = "https://yts.mx/browse-movies/0/all/all/0/featured/0/all"
        movies = []
        num_of_pages = 15
        for page in range(1, num_of_pages + 1):
            page = (num_of_pages + 1) - page
            if page > 1:
                URL = URL + '?page=' + str(page)
            
            

            r = requests.get(URL).text
            soup = BeautifulSoup(r, "lxml")
            movies_per_page = soup.findAll('div', class_="browse-movie-wrap col-xs-10 col-sm-4 col-md-5 col-lg-4")
            for name in movies_per_page[::-1]:
                mov_name = name.find('div', class_="browse-movie-bottom")

                #Get Movie Rating
                try:
                    rating = name.find('h4', class_="rating").text
                    rating = rating[:3]

                    if(rating[2] == '/'):
                        rating = rating[0:2]
                except:
                    rating = None

                movie_name = mov_name.a.text
                movie_year = mov_name.div.text
                movie_name_ = movie_name + " " + movie_year
                movie_name_ = re.sub("[\(\[].*?[\)\]]","", movie_name_)
                movie_name_ = movie_name_.lstrip()
                movie_name_ = movie_name_.replace(" ", "-")
                index = 0

                for char in movie_name_:     #handle special characters in the url
                    if char.isalnum()==False and char != "-":
                        movie_name_ = movie_name_.replace(char,"")
                for char in movie_name_:
                    if char == "-" and movie_name_[index+1]=="-":
                        movie_name_ = movie_name_[:index]+movie_name_[index+1:]
                    if(index < len(movie_name_)-1):   
                        index = index+1
                        
                
                movie_url = "https://yts.am/movie/" + movie_name_
                
                movie_url = movie_url.lower()

                request = requests.get(movie_url).text
                n_soup = BeautifulSoup(request, "lxml")
                        

                try:
                    
                    movie_sub_info = n_soup.find('div', id="movie-sub-info") 

                    screenshots_tag = n_soup.find('div', id="screenshots")
                    screenshot_links = []
                    for screenshot in screenshots_tag.findAll('div', class_='screenshot'):
                        screenshot_link = screenshot.find('a', class_='screenshot-group')['href']
                        screenshot_links.append(screenshot_link)
                    synopsis_tag = movie_sub_info.find('div',id='synopsis')
                    synopsis = synopsis_tag.find('p', class_='hidden-sm hidden-md hidden-lg').text
                except:
                    screenshot_links = []
                    synopsis = None
                    pass
                movie_name = mov_name.a.text
                movie_year = movie_year
                
                
                print('Movie Name: ', movie_name)
                print('Year: ', movie_year)
                print('Rating: ', rating)
                print('Synopsis: ', synopsis)
                print("Screenshot_links: ", screenshot_links)

                info = n_soup.find('div', class_="bottom-info")
                
                try:
                    genre = n_soup.findAll('h2')[1].text
                    imdb_link = info.find('a', title="IMDb Rating")['href']
                except:
                    genre = None
                    imdb_link = None
                    pass
                
                

                try:
                    req = requests.get(imdb_link).text
                    souper = BeautifulSoup(req, "lxml")
                    poster = souper.find('div', class_="poster")
                    a_tag = poster.find('a')
                    try:
                        plot_summary = souper.find('div', class_="plot_summary")
                        summary_text = plot_summary.find('div', class_='summary_text').text
                        summary_text = summary_text.lstrip()
                        image_link = a_tag.find('img')['src']
                    except:
                        summary_text = None
                        image_link = None
                    try:
                        stars = []
                        stars_tag = plot_summary.findAll('div', class_ = 'credit_summary_item')[2]
                        director_tag = plot_summary.findAll('div', class_ = 'credit_summary_item')[0]
                        director = director_tag.find('a').text
                        for star_ in stars_tag.findAll('a'):
                            
                            star = star_.text
                            if star == 'See full cast & crew':
                                pass
                            else:
                                stars.append(star)
                    
                    except:
                        try:
                            stars = []
                            stars_tag = plot_summary.find('div', class_ = 'credit_summary_item')
                            for star_ in stars_tag.findAll('a'):
                                
                                star = star_.text
                                if star == 'See full cast & crew':
                                    pass
                                else:
                                    stars.append(star)
                                    director = None
                        except:
                            stars = []
                            director = None
                    

                except:
                    
                    image_link = None
                    summary_text = None
                    stars = []
                    director = None
                            
                torrent_720 = None
                torrent_1080 = None
                try:
                    torrent_info = n_soup.find('p', class_="hidden-xs hidden-sm")
                    for torrent in torrent_info.findAll('a'):
                        
                        if(torrent.text[:3] == "720"):
                            #according to yts, WEB = losslessly ripped from a streaming service, same quality as BluRay
                            torrent_720 = torrent['href']
                        if(torrent.text[:4] == "1080"):
                            torrent_1080 = torrent['href']
                except:
                    torrent_720 = None
                    torrent_1080 = None
                    
                print("Genre: ", genre)
                print('Director: ', director)
                print('Stars: ', stars)
                print('Summary: ', summary_text)
                print('Image: ', image_link)
                print("IMDb link:", imdb_link)
                print("720p torrent:", torrent_720)
                print("1080p torrent:", torrent_1080)
                if torrent_720 or torrent_1080:
                    
                    
                    movie = Movie.objects.filter(title=movie_name, slug=movie_name_.lower(), year=int(movie_year)).first()
                    if not movie and movie==None:
                        movie = Movie.objects.create(title=movie_name, slug=movie_name_.lower(), year=int(movie_year), rating=rating, 
                        image_link=image_link, summary=summary_text, synopsis=synopsis, director=director, imdb_link=imdb_link,
                        torrent_720p=torrent_720, torrent_1080p=torrent_1080)

                        for name in stars:
                            star = Star.objects.filter(name=name).first()
                            if not star:
                                star = Star.objects.create(name=name)
                            sleep(1)
                            movie.stars.add(star)
                        genres = genre.split('/')
                        for genre in genres:
                            if genre and genre != ' ':
                                print(genre)
                                genre_ = genre.lstrip().rstrip()
                                genre_slug = genre_.lower().replace('/','-')
                                genre_slug = genre_.lower().replace(' ','-')
                                genre = Genre.objects.filter(name=genre_).first()
                                if not genre:
                                    genre = Genre.objects.create(name=genre_, slug=genre_slug)
                                sleep(1)
                                movie.genres.add(genre)

                    

                    for link in screenshot_links:
                        screenshot_link = Screenshot.objects.filter(movie=movie, link=link).first()
                        if not screenshot_link:
                            Screenshot.objects.create(movie=movie, link=link)
                        sleep(1)
                    


                    sleep(5)
                else:
                    pass
                    
                #rating = rating
                #movie_name = movie_name
                #movie_slug = movie_name_
                #movie_year = movie_year
                #synopsis = synopsis
                #screenshot_links = screenshot_links
                #genre = genre
                #imdb_link = imdb_link
                #summary_text = summary_text
                #image_link = image_link
                #stars = stars
                #director = director
                #torrent_720p = torrent_720
                #torrent_1080p = torrent_1080

        self.stdout.write('Scraping Complete')
                    