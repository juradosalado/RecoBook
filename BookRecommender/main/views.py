import datetime
from django.shortcuts import render
from main.RS import *
from main.models import Author, Setting

import json
from django.http import JsonResponse

from main.populateDB import populate

# Create your views here.

from django.template.defaulttags import register

from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'base_INDEX.html')

def populateDatabase(request):
    (b, g, s, a)=populate()

    message = 'It has been loaded ' + str(b) + ' books; ' + str(g) + ' genres; ' + str(s) + ' settings; ' + str(a) + ' authors.'
    return render(request, 'base_POPULATEDB.html', {'title': 'End of database load', 'message':message})

def recommend(request):
    setting = Setting.objects.filter(Q(name__icontains='Ireland'))
    genres = Genre.objects.filter(Q(name='Fantasy'))
    #declare date 7th April 2017
    date_before = datetime.date(2023, 4, 7)
    date_after = datetime.date(2010, 4, 7)
    author = Author.objects.get(name='Stephen King')
    authors = [author]
    reset_scores()
    add_age_score(17, 4)
    add_genres_score(genres, 10)
    add_author_score(author, 2)
    # add_similar_authors_score(authors, 6)
    #add_setting_score(setting, 5)
    add_pages_number_score(500, 5)
    add_rating_score(4, 10)
    add_date_score(date_after, date_before, 4)
    #it will order books first by score. Then, ties result will be ordered by rating.
    #Finally, ties result will be ordered by number of ratings (first the ones with less number of ratings)
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    return render(request, 'base_RECOMMEND_FORM.html', {'dict': dict_ordered, 'dict_matching': dictMatching})

def details(request,id):
    book = Book.objects.get(book_id=id)
    return render(request, 'base_DETAILS.html', {'book': book})

@csrf_exempt
def webhook(request):
    req = json.loads(request.body)
    intent = req['queryResult']['intent']['displayName']
    #get the entities from the request:
    parameters = req['queryResult']['parameters']
    #get the age:
    print(parameters)
    response= {
        
    }
    if intent == 'UserProvidesName':
        response = userProvidesName(parameters)
    if intent == 'UserProvidesUserAge':
        response = userProvidesUserAge(parameters)
    if intent == 'UserProvidesUserAgeRelevance':
        response = userProvidesUserAgeRelevance(parameters)
    return JsonResponse(response)

def userProvidesName(parameters):
    reset_scores()
    name = parameters['person']['name']
    text = "Nice to meet you, " +name+"! Let's start with the questions that will help me find you a new book to read. How old are you? It is important for you to know that, for every question I ask you, you do not have to answer me if you don't want to, or just don't care about it. In that case, just let me know you would rather not to response."
    print(text)
    response = {
            'fulfillmentText': text
        }
    return response

dict_parameters = dict()

def userProvidesUserAge(parameters):
    age = parameters['number-integer']
    dict_parameters['age'] = age
    response = {
    }
    return response

def userProvidesUserAgeRelevance(parameters):
    relevance = parameters['number-integer']
    dict_parameters['ageRelevance'] = relevance
    add_age_score(dict_parameters['age'], dict_parameters['ageRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    text = "Here are the books I recommend you:" + str(dict_ordered)
    print(text)
    response = {
            'fulfillmentText': text
    }

    return response

