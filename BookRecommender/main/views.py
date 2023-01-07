import datetime
from django.shortcuts import render
from main.RS import *
from main.models import Author, Setting

from main.populateDB import populate

# Create your views here.

def index(request):
    return render(request, 'base_INDEX.html')

def populateDatabase(request):
    (b, g, s, a)=populate()

    message = 'It has been loaded ' + str(b) + ' books; ' + str(g) + ' genres; ' + str(s) + ' settings; ' + str(a) + ' authors.'
    return render(request, 'base_POPULATEDB.html', {'title': 'End of database load', 'message':message})

def recommend(request):
    setting = Setting.objects.filter(Q(name__icontains='Ireland'))
    genres = Genre.objects.filter(Q(name__icontains='Fantasy'))
    #declare date 7th April 2017
    date_before = datetime.date(2006, 4, 7)
    date_after = datetime.date(2007, 4, 7)
    author = Author.objects.get(name='Stephen King')
    authors = [author]
    reset_scores()
    #add_age_score(21, 9)
    #add_genres_score(genres, 8)
    #add_setting_score(setting, 10)
    #add_pages_number_score(300, 5)
    #add_rating_score(4, 6)
    add_author_score(author, 10)
    #add_date_before_score(date_before, 4)
    #add_date_after_score(date_after, 4)
    #add_similar_authors_score(authors, 10)
    dictOrdered = dict(sorted(dictScores.items(), key=lambda item: -item[1]))
    return render(request, 'base_RECOMMEND_FORM.html', {'dict': dictOrdered})