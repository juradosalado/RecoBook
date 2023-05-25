

from main.RS import *
import time
from django.utils import timezone

from main.models import UserSession

def getResultsResponse(user_session):
    return {
        "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Great! That's everything I need. I just travelled through Narnia, the Seven Kingdoms and even the whole Cosmere looking for the perfect books for you... This is what I found!"
                        ]
                    }
                },
                {
                    "payload": {
                        "richContent": [
                            [
                            
                            
                            {
                                "icon": {
                                "type": "chevron_right",
                                "color": "#FF9800"
                                },
                                "link": "http://localhost:8000/results/"+str(user_session.session_id),
                                "text": "Check Results",
                                "event": {
                                "languageCode": "en",
                                "name": "",
                                "parameters": {}
                                },
                                "type": "button"
                            }
                            ]
                        ]
                    }
                },
                {
                "text": {
                    "text": ["Great! That's everything I need. I just travelled through Narnia, the Seven Kingdoms and even the whole Cosmere looking for the perfect books for you... This is what I found! http://localhost:8000/results/"+str(user_session.session_id)],
                },
                "platform": "TELEGRAM"
                }
        ]
    }

def isRelevanceValid(relevance, user_session, context):
    if int(relevance) <=0 or int(relevance) >10:
        response = {
            "fulfillmentText": "Oops. I need your relevance degree to be a number between 1 and 10. Please, respond with a number between 1 and 10",
        }
        return False, response
    else:
        return True, {}
    
def is_lost(user_session):
    response = {
            "fulfillmentText": "I'm very sorry, but I think I got lost in the conversation, would you mind to start over again? What was your name, dear reader?",
            "outputContexts": [{
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/UserProvidesNameContext',
                "lifespanCount": 5, 
                "parameters": {
                }
            }]
        }
    return response

def welcome(user_session):
    if user_session not in dictScores:
        dictScores[user_session] = dict()
        for book in Book.objects.all():
            dictScores[user_session][book] = 0
    if user_session not in dictMatching:
        dictMatching[user_session] = dict()
    reset_scores(user_session)
    user_session.date_last_used = timezone.now()
    response = {
        "outputContexts": [{
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/HowDoIWorkContext',
                "lifespanCount": 5, 
                "parameters": {
                }
            },
            {
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/NotHowDoIWorkContext',
                "lifespanCount": 5,
                "parameters": {
                }
            }]
    }
    return response

def userProvidesName(parameters, user_session):
    name = parameters['person']['name']
    user_session.name = name
    user_session.save()
    text = "Nice to meet you, " +name+"! Let's start with the questions that will help me find you a new book to read. How old are you? If you don't want your age to be relevant in the recommendation, pleasy type 'skip'."
    response = {
            'fulfillmentText': text,
            'session': user_session.session_id
        }
    return response



def userProvidesUserAge(parameters, user_session):
    session_id = user_session.session_id
    age = parameters['number-integer']
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.age = age
    user_session.save()
    response = {
        'session': session_id
    }
    return response

def userProvidesUserAgeRelevance(parameters, user_session, intent):
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session, 'UserProvidesAgeRelevanceContext')
    if not isRelValid:
        return response
    session_id = user_session.session_id
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.age_relevance = relevance
    user_session.is_waiting = True
    user_session.save()
    add_age_score(user_session)
    response = {
        'session': session_id
    }
    return response

def userProvidesGenres(parameters, user_session):
    session_id = user_session.session_id
    genres_list = parameters['genre']
    genres = Genre.objects.filter(Q(name__in=genres_list))
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.genres.set(genres)
    user_session.save()
    response = {
        'session': user_session.session_id
    }
    
    return response

def userProvidesGenresRelevance(parameters, user_session):
    session_id = user_session.session_id
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session, 'UserProvidesGenresRelevanceContext')
    if not isRelValid:
        return response
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.genres_relevance = int(relevance)
    user_session.save()
    waiting = user_session.is_waiting
    while(waiting):
        time.sleep(3)
        user_session = UserSession.objects.get(session_id=session_id)
        waiting = user_session.is_waiting
    user_session.is_waiting = True
    user_session.save()
    add_genres_score(user_session)
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesAuthor(parameters, user_session):
    session_id = user_session.session_id
    author_name = parameters['person']['name']
    author = Author.objects.filter(name__icontains=author_name)
    user_session = UserSession.objects.get(session_id=session_id)
    if author:
        user_session.author_name = str(author[0])
    else:
        user_session.author_name = None
    user_session.save()

    response = {'fulfillmentText': "From one to ten, how much importance do you want the fact that a book is written by " + author_name+" to have in your book recommendation",
        'session': user_session.session_id
    }
    return response

def userProvidesAuthorRelevance(parameters, user_session):
    session_id = user_session.session_id
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session, 'UserProvidesAuthorRelevanceContext')
    if not isRelValid:
        return response
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.author_relevance = int(relevance)
    user_session.save()
    if user_session.author_name is not None:
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
    response = {
        'session': session_id
    }
    return response

def userProvidesSimilarAuthors(parameters, user_session):
    session_id = user_session.session_id
    authors_list = parameters
    query = Q()
    for author in authors_list['person']:
        query |= Q(name__icontains=author['name'])
    authors = Author.objects.filter(query)
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.similar_authors.set(authors)
    user_session.save()

    response = {
        'session': session_id
    }
    return response

def userProvidesSimilarAuthorsRelevance(parameters, user_session):
    session_id = user_session.session_id
    relevance = parameters['number-integer']
    isRelValid, response = isRelevanceValid(relevance, user_session, 'UserProvidesSimilarAuthorsRelevanceContext')
    if not isRelValid:
        return response
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
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesSettings(parameters, user_session):
    session_id = user_session.session_id
    setting_list = parameters['settings']
    query = Q()
    for setting in setting_list:
        query |= Q(name__icontains=setting)
    settings = Setting.objects.filter(query)
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
    isRelValid, response = isRelevanceValid(relevance, user_session, 'UserProvidesSettingsRelevanceContext')
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
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesPages(parameters, user_session):
    session_id = user_session.session_id
    pages = parameters['number-integer']
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
    isRelValid, response = isRelevanceValid(relevance, user_session, 'UserProvidesPagesRelevanceContext')
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
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesRate(parameters, user_session):
    session_id = user_session.session_id
    rate = parameters["number"]
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
    isRelValid, response = isRelevanceValid(relevance, user_session, 'UserProvidesRateRelevanceContext')
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
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesDate(parameters, user_session):
    session_id = user_session.session_id
    date = parameters['date']
    dateAfter = datetime.datetime.fromisoformat(date[0])
    dateBefore = datetime.datetime.fromisoformat(date[1])
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
    isRelValid, response = isRelevanceValid(relevance, user_session, 'UserProvidesDateRelevanceContext')
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
    response = getResultsResponse(user_session)
    return response

def userProvidesDateEmpty(user_session):
    response = getResultsResponse(user_session)
    return response

def skip(user_session, outputContexts):
    if any('userprovidesdatecontext' in context['name'] for context in outputContexts):
        response = getResultsResponse(user_session)
    elif any('userprovidesratecontext' in context['name'] for context in outputContexts):
        response = {
            "fulfillmentText": "And just one more question... Are you looking for books that were published between two specific dates? You can say dates with MM/DD/YY format, or just mention two years, if you don't care about months and days.",
            "outputContexts": [{
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/UserProvidesDateContext',
                "lifespanCount": 5, 
                "parameters": {
                }
            }]
        }
    elif any('userprovidespagescontext' in context['name'] for context in outputContexts):
        response = {
            "fulfillmentText": "Great! We're almost done. Now, it's time for people to judge! What would be the minimum rate, from 1 to 5, that you would want your next read to have in the social network GoodReads?",
            "outputContexts": [{
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/UserProvidesRateContext',
                "lifespanCount": 5, 
                "parameters": {
                }
            }]
        }
    elif any('userprovidessettingscontext' in context['name'] for context in outputContexts):
        response = {
            "fulfillmentText": "I know sometimes a book length can be an important fact for readers... What would be the maximum amount of pages that you would like to find in your next read? Again, you can type 'skip' and skip this question if you don't care about this, don't be shy!",
            "outputContexts": [{
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/UserProvidesPagesContext',
                "lifespanCount": 5, 
                "parameters": {
                }
            }]
        }
    elif any('userprovidessimilarauthorscontext' in context['name'] for context in outputContexts):
        response = {
            "fulfillmentText": "Now, let's talk about settings! In wich place would you like your next favourite story to be set? You can name a city, a country or even a famous fictional place, like Neverland. Everything is possible when it comes to stories!",
            "outputContexts": [{
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/UserProvidesSettingsContext',
                "lifespanCount": 5, 
                "parameters": {
                }
            }]
        }
    elif any('userprovidesauthorcontext' in context['name'] for context in outputContexts):
        response = {
            "fulfillmentText": "In that case, are you looking for a book written by an author who's similar to another author? If so, you can name one or more than one authors, and I'll find you books with similar wrtiting styles! If you are not interested in this, please type 'skip' or tell me you are not interested in similar authors.",
            "outputContexts": [{
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/UserProvidesSimilarAuthorsContext',
                "lifespanCount": 5, 
                "parameters": {
                }
            }]
        }
    elif any('userprovidesgenrescontext' in context['name'] for context in outputContexts):
        response = {
            "fulfillmentText": "I see... So, are you looking for a book by an specific author? If so, what's the author name?",
            "outputContexts": [{
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/UserProvidesAuthorContext',
                "lifespanCount": 5, 
                "parameters": {
                }
            }]
        }
    elif any('userprovidesagecontext' in context['name'] for context in outputContexts):
        response = {
            "fulfillmentText": "Good. Now, my favourite question: what genres would you want your next read to have? You can say more than one If you want, or just type 'skip' if you don't care about genres.",
            "outputContexts": [{
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/UserProvidesGenresContext',
                "lifespanCount": 5, 
                "parameters": {
                }
            }]
        }
    else:
        response = {
            "fulfillmentText": "Cool, let's start with the questions that will help me find you a new book to read. How old are you? If you don't want your age to be relevant in the recommendation, pleasy type 'skip'",
            "outputContexts": [{
                "name": 'projects/william-qxgh/agent/sessions/'+user_session.session_id+'/contexts/UserProvidesAgeContext',
                "lifespanCount": 5, 
                "parameters": {
                }
            }]
        }
    return response

