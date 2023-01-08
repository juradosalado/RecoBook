import datetime
from django.shortcuts import render
from main.RS import *
from main.models import Author, Setting

from main.populateDB import populate

# Create your views here.

from django.template.defaulttags import register


def index(request):
    return render(request, 'base_INDEX.html')

def populateDatabase(request):
    (b, g, s, a)=populate()

    message = 'It has been loaded ' + str(b) + ' books; ' + str(g) + ' genres; ' + str(s) + ' settings; ' + str(a) + ' authors.'
    return render(request, 'base_POPULATEDB.html', {'title': 'End of database load', 'message':message})

def recommend(request):
    setting = Setting.objects.filter(Q(name__icontains='Ireland'))
    genres = Genre.objects.filter(Q(name='LGBT'))
    #declare date 7th April 2017
    date_before = datetime.date(2023, 4, 7)
    date_after = datetime.date(2010, 4, 7)
    author = Author.objects.get(name='Cassandra Clare')
    authors = [author]
    reset_scores()
    #add_age_score(17, 4)
    add_genres_score(genres, 10)
    #add_setting_score(setting, 5)
    add_pages_number_score(500, 5)
    add_rating_score(4, 10)
    add_author_score(author, 2)
    #add_date_before_score(date_before, 1)
    #add_date_after_score(date_after, 5)
    #add_similar_authors_score(authors, 6)
    #it will order books first by score. Then, ties result will be ordered by rating.
    #Finally, ties result will be ordered by number of ratings (first the ones with less number of ratings)
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    return render(request, 'base_RECOMMEND_FORM.html', {'dict': dict_ordered, 'dict_matching': dictMatching})