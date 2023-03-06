

from main.RS import *
import time
waiting = True
def userProvidesName(parameters, user_session):
    session_id = user_session.session_id
    reset_scores(user_session)
    name = parameters['person']['name']
    user_session.name = name
    user_session.save()
    #dict_parameters['userName'] = name
    text = "Nice to meet you, " +name+"! Let's start with the questions that will help me find you a new book to read. How old are you? It is important for you to know that, for every question I ask you, you do not have to answer me if you don't want to, or just don't care about it. In that case, just let me know you would rather not to response."
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
    user_session.age = age
    user_session.save()
    print("User age:"+str(age))
    response = {
        'session': session_id
    }
    return response

def userProvidesUserAgeRelevance(parameters, user_session):
    relevance = parameters['relevance']
    session_id = user_session.session_id
    user_session.age_relevance = relevance
    user_session.save()
    print("User age relevance: "+str(relevance))
    waiting = True
    add_age_score(user_session)
    waiting = False
    response = {
        'session': session_id
    }
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    return response

def userProvidesGenres(parameters, user_session):
    genres_list = parameters['genre']
    #Get all genres that contains the names in the list genres:
    genres = Genre.objects.filter(Q(name__in=genres_list))
    user_session.genres.set(genres)
    user_session.save()
    print("User genres: "+str(genres))
    response = {
        'session': user_session.session_id
    }
    
    return response

def userProvidesGenresRelevance(parameters, user_session):
    print("Entré")
    relevance = parameters['number-integer']
    user_session.genres_relevance = int(relevance)
    user_session.save()
    print("User genres relevance: "+str(relevance))
    while(waiting):
        print("Waiting")
        time.sleep(3)

    add_genres_score(user_session)
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesAuthor(parameters, user_session):
    author_name = parameters['person']['name']
    author = Author.objects.get(name=author_name)
    print("User author: "+str(author))
    dict_parameters['author'] = author
    response = {'fulfillmentText': "From one to ten, how much importance do you want the fact that a book is written by " + author_name+" to have in your book recommendation",
        'session': user_session.session_id
    }
    return response

def userProvidesAuthorRelevance(parameters, user_session):
    relevance = parameters['relevance']
    dict_parameters['authorRelevance'] = float(relevance)
    print("User author relevance: "+str(relevance))
    #print type of dict_parameters['auhtorRelevance']:
    print(type(dict_parameters['authorRelevance']))
    add_author_score(dict_parameters['author'], dict_parameters['authorRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesSimilarAuthors(parameters, user_session):
    authors_list = parameters
    #get the names of authors:
    query = Q()
    for author in authors_list['person']:
        query |= Q(name__icontains=author['name'])
    authors = Author.objects.filter(query)

    print("User similar authors: "+str(authors))
    dict_parameters['similarAuthors'] = authors
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesSimilarAuthorsRelevance(parameters, user_session):
    relevance = parameters['number-integer']
    dict_parameters['similarAuthorsRelevance'] = int(relevance)
    print("User similar authors relevance: "+str(relevance))
    print(dict_parameters)
    add_similar_authors_score(dict_parameters['similarAuthors'], dict_parameters['similarAuthorsRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesSettings(parameters, user_session):
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
        'session': user_session.session_id
    }
    return response

def userProvidesSettingsRelevance(parameters, user_session):
    name = dict_parameters['userName']
    print(name)
    relevance = parameters['number-integer']
    dict_parameters['settingsRelevance'] = int(relevance)
    print("User settings relevance: "+str(relevance))
    add_settings_score(dict_parameters['settings'], dict_parameters['settingsRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'fulfillmentText': "I know sometimes a book length can be an important fact for readers... What would be the maximum amount of pages that you would like to find in your next read? Again, you can let me know that you don't care about this if that's the case, don't be shy,"+ name+"!",
        'session': user_session.session_id
    }
    return response

def userProvidesPages(parameters, user_session):
    pages = parameters['number-integer']
    print("User pages: "+str(pages))
    dict_parameters['pages'] = pages
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesPagesRelevance(parameters, user_session):
    relevance = parameters['number-integer']
    dict_parameters['pagesRelevance'] = int(relevance)
    print("User pages relevance: "+str(relevance))
    add_pages_number_score(dict_parameters['pages'], dict_parameters['pagesRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesRate(parameters, user_session):
    rating = parameters['number']
    print("User rating: "+str(rating))
    dict_parameters['rating'] = float(rating)
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesRateRelevance(parameters, user_session):
    relevance = parameters['number-integer']
    dict_parameters['ratingRelevance'] = int(relevance)
    print("User rating relevance: "+str(relevance))
    add_rating_score(dict_parameters['rating'], dict_parameters['ratingRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesDate(parameters, user_session):
    date = parameters['date']
    dateAfter = datetime.fromisoformat(date[0]).date()
    dateBefore = datetime.fromisoformat(date[1]).date()
    #print type of date:
    print(type(date))
    print("User date: "+str(date))
    dict_parameters['dateAfter'] = dateAfter
    dict_parameters['dateBefore'] = dateBefore
    response = {
        'session': user_session.session_id
    }
    return response

def userProvidesDateRelevance(parameters, user_session):
    relevance = parameters['number-integer']
    dict_parameters['dateRelevance'] = int(relevance)
    print("User date relevance: "+str(relevance))
    add_date_score(dict_parameters['dateAfter'], dict_parameters['dateBefore'], dict_parameters['dateRelevance'])
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(str(dict_ordered))
    response = {
        'session': user_session.session_id
    }
    return response