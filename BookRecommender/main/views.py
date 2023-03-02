import datetime
from django.shortcuts import render
from main.RS import *
from main.models import Author, Setting
from datetime import datetime

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
    #add_settings_score(setting, 5)
    add_pages_number_score(500, 5)
    add_rating_score(4, 10)
    add_date_score(date_after, date_before, 4)
    #it will order books first by score. Then, ties result will be ordered by rating.
    #Finally, ties result will be ordered by number of ratings (first the ones with less number of ratings)
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    return render(request, 'base_RECOMMEND_FORM.html', {'dict': dict_ordered, 'dict_matching': dictMatching})

def showResults(request):
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(dict_ordered)
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
    if intent == 'UserProvidesGenres':
        response = userProvidesGenres(parameters)
    if intent == 'UserProvidesGenresRelevance':
        response = userProvidesGenresRelevance(parameters)
    if intent == 'UserProvidesAuthor':
        response = userProvidesAuthor(parameters)
    if intent == 'UserProvidesAuthorRelevance':
        response = userProvidesAuthorRelevance(parameters)
    if intent == 'UserProvidesSimilarAuthors2':
        response = userProvidesSimilarAuthors(parameters)
    if intent == 'UserProvidesSimilarAuthorsRelevance':
        response = userProvidesSimilarAuthorsRelevance(parameters)
    if intent == 'UserProvidesSettings':
        response = userProvidesSettings(parameters)
    if intent == 'UserProvidesSettingsRelevance':
        response = userProvidesSettingsRelevance(parameters)
    if intent == 'UserProvidesPages':
        response = userProvidesPages(parameters)
    if intent == 'UserProvidesPagesRelevance':
        response = userProvidesPagesRelevance(parameters)
    if intent == 'UserProvidesRate':
        response = userProvidesRate(parameters)
    if intent == 'UserProvidesRateRelevance':
        response = userProvidesRateRelevance(parameters)
    if intent == 'UserProvidesDate':
        response = userProvidesDate(parameters)
    if intent == 'UserProvidesDateRelevance':
        response = userProvidesDateRelevance(parameters)


    
    return JsonResponse(response)

dict_parameters = dict()

def userProvidesName(parameters):
    reset_scores()
    name = parameters['person']['name']
    dict_parameters['userName'] = name
    text = "Nice to meet you, " +name+"! Let's start with the questions that will help me find you a new book to read. How old are you? It is important for you to know that, for every question I ask you, you do not have to answer me if you don't want to, or just don't care about it. In that case, just let me know you would rather not to response."
    print(text)
    response = {
            'fulfillmentText': text
        }
    return response



def userProvidesUserAge(parameters):
    age = parameters['number-integer']
    print("User age:"+str(age))
    dict_parameters['age'] = age
    response = {
    }
    return response

def userProvidesUserAgeRelevance(parameters):
    relevance = parameters['relevance']
    dict_parameters['ageRelevance'] = int(relevance)
    print("User age relevance: "+str(relevance))
    add_age_score(dict_parameters['age'], dict_parameters['ageRelevance'])
    response = {
    }
    return response

def userProvidesGenres(parameters):
    genres_list = parameters['genre']
    #Get all genres that contains the names in the list genres:
    genres = Genre.objects.filter(Q(name__in=genres_list))
    print("User genres: "+str(genres))
    dict_parameters['genres'] = genres
    response = {
    }
    return response

def userProvidesGenresRelevance(parameters):
    relevance = parameters['number-integer']
    dict_parameters['genresRelevance'] = int(relevance)
    print("User genres relevance: "+str(relevance))
    add_genres_score(dict_parameters['genres'], dict_parameters['genresRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
    }
    return response

def userProvidesAuthor(parameters):
    author_name = parameters['person']['name']
    author = Author.objects.get(name=author_name)
    print("User author: "+str(author))
    dict_parameters['author'] = author
    response = {'fulfillmentText': "From one to ten, how much importance do you want the fact that a book is written by " + author_name+" to have in your book recommendation"
    }
    return response

def userProvidesAuthorRelevance(parameters):
    relevance = parameters['relevance']
    dict_parameters['authorRelevance'] = float(relevance)
    print("User author relevance: "+str(relevance))
    #print type of dict_parameters['auhtorRelevance']:
    print(type(dict_parameters['authorRelevance']))
    add_author_score(dict_parameters['author'], dict_parameters['authorRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
    }
    return response

def userProvidesSimilarAuthors(parameters):
    authors_list = parameters
    #get the names of authors:
    query = Q()
    for author in authors_list['person']:
        query |= Q(name__icontains=author['name'])
    authors = Author.objects.filter(query)

    print("User similar authors: "+str(authors))
    dict_parameters['similarAuthors'] = authors
    response = {
    }
    return response

def userProvidesSimilarAuthorsRelevance(parameters):
    relevance = parameters['number-integer']
    dict_parameters['similarAuthorsRelevance'] = int(relevance)
    print("User similar authors relevance: "+str(relevance))
    print(dict_parameters)
    add_similar_authors_score(dict_parameters['similarAuthors'], dict_parameters['similarAuthorsRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
    }
    return response

def userProvidesSettings(parameters):
    setting_list = parameters['settings']
    #Get all settings that contains the names in the list settings:
    #not name == setting, but name like setting

    query = Q()
    for setting in setting_list:
        query |= Q(name__icontains=setting)
    settings = Setting.objects.filter(query)
    print("User settings: "+str(settings))
    dict_parameters['settings'] = settings
    response = {
    }
    return response

def userProvidesSettingsRelevance(parameters):
    name = dict_parameters['userName']
    print(name)
    relevance = parameters['number-integer']
    dict_parameters['settingsRelevance'] = int(relevance)
    print("User settings relevance: "+str(relevance))
    add_settings_score(dict_parameters['settings'], dict_parameters['settingsRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'fulfillmentText': "I know sometimes a book length can be an important fact for readers... What would be the maximum amount of pages that you would like to find in your next read? Again, you can let me know that you don't care about this if that's the case, don't be shy,"+ name+"!"
    }
    return response

def userProvidesPages(parameters):
    pages = parameters['number-integer']
    print("User pages: "+str(pages))
    dict_parameters['pages'] = pages
    response = {
    }
    return response

def userProvidesPagesRelevance(parameters):
    relevance = parameters['number-integer']
    dict_parameters['pagesRelevance'] = int(relevance)
    print("User pages relevance: "+str(relevance))
    add_pages_number_score(dict_parameters['pages'], dict_parameters['pagesRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
    }
    return response

def userProvidesRate(parameters):
    rating = parameters['number']
    print("User rating: "+str(rating))
    dict_parameters['rating'] = float(rating)
    response = {
    }
    return response

def userProvidesRateRelevance(parameters):
    relevance = parameters['number-integer']
    dict_parameters['ratingRelevance'] = int(relevance)
    print("User rating relevance: "+str(relevance))
    add_rating_score(dict_parameters['rating'], dict_parameters['ratingRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
    }
    return response

def userProvidesDate(parameters):
    date = parameters['date']
    dateAfter = datetime.fromisoformat(date[0]).date()
    dateBefore = datetime.fromisoformat(date[1]).date()
    #print type of date:
    print(type(date))
    print("User date: "+str(date))
    dict_parameters['dateAfter'] = dateAfter
    dict_parameters['dateBefore'] = dateBefore
    response = {
    }
    return response

def userProvidesDateRelevance(parameters):
    relevance = parameters['number-integer']
    dict_parameters['dateRelevance'] = int(relevance)
    print("User date relevance: "+str(relevance))
    add_date_score(dict_parameters['dateAfter'], dict_parameters['dateBefore'], dict_parameters['dateRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
    }
    return response

#TODO:
#limitar relevancias entre 1 y 10
#rating que no se salga de 1 y 5
#eliminar relevance
#Mensaje de formato de fechas
#boton que redirija a resultados.
#Refactorizar




