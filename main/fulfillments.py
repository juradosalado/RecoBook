

from main.RS import *
import time
from django.utils import timezone

from main.models import UserSession

def isRelevanceValid(relevance, user_session):
    print("No es valido colega")
    if int(relevance) <=0 or int(relevance) >10:
        response={
            'fulfillmentText': "Oops. I need your relevance degree to be a number between 1 and 10. Please, respond with a number between 1 and 10",
            'session': user_session.session_id

        }
        return False, response
    else:
        return True, {}


def userProvidesName(parameters, user_session):
    session_id = user_session.session_id
    reset_scores(user_session)
    #set user_session date_last_used to right now:
    user_session.date_last_used = timezone.now()
    name = parameters['person']['name']
    user_session.name = name
    user_session.save()
    #dict_parameters['userName'] = name
    text = "Nice to meet you, " +name+"! Let's start with the questions that will help me find you a new book to read. How old are you? It is important for you to know that, for every question I ask you, you do not have to answer me if you don't want to, or just don't care about it. In that case, just let me know by saying: 'I don't care about my age'."
    #print(text)
    response = {
            'fulfillmentText': text,
            'session': session_id
        }
    return response



def userProvidesUserAge(parameters, user_session):
    print(user_session.name)
    session_id = user_session.session_id
    age = parameters['number-integer']
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.age = age
    user_session.save()
    print("User age:"+str(age))
    response = {
        'session': session_id
    }
    return response

def userProvidesUserAgeRelevance(parameters, user_session, intent):
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session)
    if not isRelValid:
        return response
    session_id = user_session.session_id
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.age_relevance = relevance
    print("User age relevance: "+str(relevance))
    user_session.is_waiting = True
    user_session.save()
    add_age_score(user_session)
    response = {
        'session': session_id
    }
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    return response

def userProvidesGenres(parameters, user_session):
    session_id = user_session.session_id
    genres_list = parameters['genre']
    #Get all genres that contains the names in the list genres:
    genres = Genre.objects.filter(Q(name__in=genres_list))
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.genres.set(genres)
    user_session.save()
    print("User genres: "+str(genres))
    response = {
        'session': user_session.session_id
    }
    
    return response

def userProvidesGenresRelevance(parameters, user_session):
    session_id = user_session.session_id
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session)
    if not isRelValid:
        return response
    print("Entré")
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.genres_relevance = int(relevance)
    user_session.save()
    print("User genres relevance: "+str(relevance))
    waiting = user_session.is_waiting
    while(waiting):
        time.sleep(3)
        user_session = UserSession.objects.get(session_id=session_id)
        waiting = user_session.is_waiting
    user_session.is_waiting = True
    user_session.save()
    add_genres_score(user_session)
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesAuthor(parameters, user_session):
    session_id = user_session.session_id
    author_name = parameters['person']['name']
    print(author_name)
    author = Author.objects.filter(name__icontains=author_name)
    print(author[0])
    #check that author contains any object:
    user_session = UserSession.objects.get(session_id=session_id)
    if author:
        user_session.author_name = str(author[0])
    else:
        user_session.author_name = None
    user_session.save()
    print(user_session.author_name)

    response = {'fulfillmentText': "From one to ten, how much importance do you want the fact that a book is written by " + author_name+" to have in your book recommendation",
        'session': user_session.session_id
    }
    return response

def userProvidesAuthorRelevance(parameters, user_session):
    session_id = user_session.session_id
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session)
    if not isRelValid:
        return response
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.author_relevance = int(relevance)
    print(user_session.author_name)
    user_session.save()
    if user_session.author_name is not None:
        print("Voy a puntuar el autor:")
        waiting = user_session.is_waiting
        while(waiting):
            user_session = UserSession.objects.get(session_id=session_id)
            waiting = user_session.is_waiting
            time.sleep(3)
        user_session = UserSession.objects.get(session_id=session_id)
        user_session.is_waiting = True
        user_session.save()
        add_author_score(user_session)
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': session_id
    }
    return response

def userProvidesSimilarAuthors(parameters, user_session):
    session_id = user_session.session_id
    authors_list = parameters
    #get the names of authors:
    query = Q()
    for author in authors_list['person']:
        query |= Q(name__icontains=author['name'])
    authors = Author.objects.filter(query)
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.similar_authors.set(authors)
    user_session.save()
    print("User similar authors: "+str(authors))

    response = {
        'session': session_id
    }
    return response

def userProvidesSimilarAuthorsRelevance(parameters, user_session):
    session_id = user_session.session_id
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session)
    if not isRelValid:
        return response
    print("User similar authors relevance: "+str(relevance))
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.similar_authors_relevance = int(relevance)
    user_session.save()
    waiting = user_session.is_waiting
    while(waiting):
        time.sleep(3)
        user_session = UserSession.objects.get(session_id=session_id)
        waiting = user_session.is_waiting
    user_session.is_waiting = True
    user_session.save()
    add_similar_authors_score(user_session)
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesSettings(parameters, user_session):
    session_id = user_session.session_id
    setting_list = parameters['settings']
    #Get all settings that contains the names in the list settings:
    #not name == setting, but name like setting

    query = Q()
    for setting in setting_list:
        query |= Q(name__icontains=setting)
    settings = Setting.objects.filter(query)
    print("User settings: "+str(settings))
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.settings.set(settings)
    user_session.save()
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesSettingsRelevance(parameters, user_session):
    session_id = user_session.session_id
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session)
    if not isRelValid:
        return response
    user_session = UserSession.objects.get(session_id=session_id)
    waiting = user_session.is_waiting
    while(waiting):
        time.sleep(3)
        user_session = UserSession.objects.get(session_id=session_id)
        waiting = user_session.is_waiting
    user_session.settings_relevance = int(relevance)
    user_session.is_waiting = True
    user_session.save()
    add_settings_score(user_session)
    print("User settings relevance: "+str(relevance))
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesPages(parameters, user_session):
    session_id = user_session.session_id
    pages = parameters['number-integer']
    print("User pages: "+str(pages))
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.pages_number = int(pages)
    user_session.save()
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesPagesRelevance(parameters, user_session):
    session_id = user_session.session_id
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session)
    if not isRelValid:
        return response
    waiting = user_session.is_waiting
    while(waiting):
        time.sleep(3)
        user_session = UserSession.objects.get(session_id=session_id)
        waiting = user_session.is_waiting
    user_session.is_waiting = True
    user_session.pages_number_relevance = int(relevance)
    user_session.save()
    add_pages_number_score(user_session)
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesRate(parameters, user_session):
    session_id = user_session.session_id
    rate = parameters["number"]
    print("User rate: "+str(rate))
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.rating = float(rate)
    user_session.save()
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesRateRelevance(parameters, user_session):
    session_id = user_session.session_id
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session)
    if not isRelValid:
        return response
    waiting = user_session.is_waiting
    while(waiting):
        time.sleep(3)
        user_session = UserSession.objects.get(session_id=session_id)
        waiting = user_session.is_waiting
    user_session.is_waiting = True
    user_session.rating_relevance = int(relevance)
    user_session.save()
    add_rating_score(user_session)
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesDate(parameters, user_session):
    session_id = user_session.session_id
    date = parameters['date']
    dateAfter = datetime.datetime.fromisoformat(date[0])
    dateBefore = datetime.datetime.fromisoformat(date[1])
    #print type of date:
    print(type(date))
    print("User date: "+str(date))

    user_session = UserSession.objects.get(session_id=session_id)
    user_session.date_before = dateBefore
    user_session.date_after = dateAfter
    user_session.save()
    response = {
        'session': session_id
    }
    return response

def userProvidesDateRelevance(parameters, user_session):
    session_id = user_session.session_id
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session)
    if not isRelValid:
        return response
    waiting = user_session.is_waiting
    while(waiting):
        time.sleep(3)
        user_session = UserSession.objects.get(session_id=session_id)
        waiting = user_session.is_waiting
    user_session.is_waiting = True
    user_session.date_relevance = int(relevance)
    user_session.save()
    add_date_score(user_session)
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'fulfillmentText': "Great! That's everything I need. I just travelled through Narnia, the Seven Kingdoms and even the whole Cosmere looking for the perfect books for you... This is what i found! localhost:8000/results/?session="+str(user_session.session_id),
        'session': user_session.session_id
    }
    return response

def userProvidesDateEmpty(user_session):
    response = {
        'fulfillmentText': "Great! That's everything I need. I just travelled through Narnia, the Seven Kingdoms and even the whole Cosmere looking for the perfect books for you... This is what i found! localhost:8000/results/?session="+str(user_session.session_id),
        'session': user_session.session_id
    }
    return response
