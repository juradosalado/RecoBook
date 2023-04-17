import datetime
import uuid
from django.shortcuts import render
from BookRecommender import settings
from main.RS import *
from main.fulfillments import *
from main.models import Author, Setting, UserSession
from datetime import datetime, timedelta
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout

import json
from django.http import HttpResponseRedirect, JsonResponse

from main.populateDB import populate

# Create your views here.

from django.template.defaulttags import register

from django.views.decorators.csrf import csrf_exempt


def deleteOldUserSessions():
    OldUserSessions= UserSession.objects.filter(date_last_used__lt=datetime.now()-timedelta(days=1))
    for oldusersession in OldUserSessions:
        if oldusersession in dictScores:
            del dictScores[oldusersession]
        if oldusersession.session_id in dictMatching:
            del dictMatching[oldusersession]
    OldUserSessions.delete()

def index(request):
    #DELETE ALL UserSession with more than 24 hours since their date_created:
    #deleteOldUserSessions()
    print(dictScores)
    return render(request, 'base_INDEX.html')

def chatbot(request):
    return render(request, 'base_CHATBOT.html')

def aboutMe(request):
    return render(request, 'base_ABOUTME.html')

def login_for_populate(request):
    form = AuthenticationForm()
    if request.method=='POST':
        form = AuthenticationForm(request.POST)
        user=request.POST['username']
        password=request.POST['password']
        access=authenticate(username=user,password=password)
        if access is not None:
            if access.is_active:
                login(request, access)
                return (HttpResponseRedirect('/populate'))
            else:
                return render(request, 'mensaje_error.html',{'error':"USUARIO NO ACTIVO",'STATIC_URL':settings.STATIC_URL})
        else:
            return render(request, 'mensaje_error.html',{'error':"USUARIO O CONTRASEÑA INCORRECTOS",'STATIC_URL':settings.STATIC_URL})
                     
    return render(request, 'ingresar.html', {'form':form, 'STATIC_URL':settings.STATIC_URL})

@login_required(login_url='/login')
def populateDatabase(request):
    (b, g, s, a)=populate(request)

    message = 'It has been loaded ' + str(b) + ' books; ' + str(g) + ' genres; ' + str(s) + ' settings; ' + str(a) + ' authors.'
    return render(request, 'base_POPULATEDB.html', {'title': 'End of database load', 'message':message})

def recommend(request):
    if 'nonuser' not in request.session:
        request.session['nonuser'] = str(uuid.uuid4())
    session_id = request.session['nonuser']
    print(session_id)
    setting = Setting.objects.filter(Q(name__icontains='Ireland'))
    genres = Genre.objects.filter(Q(name='Fantasy'))
    #declare date 7th April 2017
    #date_before = datetime.date(2023, 4, 7)
    #date_after = datetime.date(2010, 4, 7)
    author = Author.objects.get(name='Stephen King')
    authors = [author]
    reset_scores()
    #add_age_score(17, 4)
    #add_genres_score(genres, 10)
    #add_author_score(author, 2)
    # add_similar_authors_score(authors, 6)
    #add_settings_score(setting, 5)
    add_pages_number_score(500, 5)
    #add_rating_score(4, 10)
    #add_date_score(date_after, date_before, 4)
    #it will order books first by score. Then, ties result will be ordered by rating.
    #Finally, ties result will be ordered by number of ratings (first the ones with less number of ratings)
    dict_ordered = dict(list(sorted(dictScores.items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    return render(request, 'base_RECOMMEND_FORM.html', {'dict': dict_ordered, 'dict_matching': dictMatching})

def showResults(request, session_id):
    user_session = UserSession.objects.get(session_id=session_id)
    dict_ordered = dict(list(sorted(dictScores[user_session].items(), key=lambda item: (-item[1], -item[0].average_rating, item[0].num_ratings)))[:20])
    print(dict_ordered)
    return render(request, 'base_RESULTS.html', {'dict': dict_ordered, 'dict_matching': dictMatching[user_session]})

def details(request,id):
    book = Book.objects.get(book_id=id)
    return render(request, 'base_DETAILS.html', {'book': book})

@csrf_exempt
def webhook(request):
    print("Empeizan prints")
    print(request.session)
    req = json.loads(request.body)
    if 'session' in req:
        print(req['session'])
        session_id = req['session'].split("/")[-1]
        print("Esta es la id:"+ session_id)
    else:
        session_id = str(uuid.uuid4())
        print("Esta es la nueva id:"+ session_id)
    user_session = UserSession.objects.filter(session_id=session_id)
    if not user_session:
        user_session = UserSession.objects.create(session_id=session_id)
        user_session.save()
    else:
        user_session = user_session[0]
    print("EL USER SESSION ES:"+str(user_session))

    outputContexts = []
    if 'outputContexts' in req['queryResult']:
        outputContexts = req['queryResult']['outputContexts']
    print(outputContexts)
    print(len(outputContexts))
    #get the name of first context:
    if len(outputContexts)==1 and any("__system_counters__" in context['name'] for context in outputContexts):
        response = is_lost(user_session)
        return JsonResponse(response)


    intent = req['queryResult']['intent']['displayName']
    #get the entities from the request:
    parameters = req['queryResult']['parameters']
    #get the age:
    print(parameters)
    response= {
        
    }
    if intent == 'Welcome':
        response = welcome(user_session)
    if intent == 'UserProvidesName':
        response = userProvidesName(parameters, user_session)
    if intent == 'UserProvidesUserAge':
        response = userProvidesUserAge(parameters, user_session)
    if intent == 'UserProvidesUserAgeRelevance':
        response = userProvidesUserAgeRelevance(parameters, user_session, intent)
    if intent == 'UserProvidesGenres':
        response = userProvidesGenres(parameters, user_session)
    if intent == 'UserProvidesGenresRelevance':
        response = userProvidesGenresRelevance(parameters, user_session)
    if intent == 'UserProvidesAuthor':
        response = userProvidesAuthor(parameters, user_session)
    if intent == 'UserProvidesAuthorRelevance':
        response = userProvidesAuthorRelevance(parameters, user_session)
    if intent == 'UserProvidesSimilarAuthors2':
        response = userProvidesSimilarAuthors(parameters, user_session)
    if intent == 'UserProvidesSimilarAuthorsRelevance':
        response = userProvidesSimilarAuthorsRelevance(parameters, user_session)
    if intent == 'UserProvidesSettings':
        response = userProvidesSettings(parameters, user_session)
    if intent == 'UserProvidesSettingsRelevance':
        response = userProvidesSettingsRelevance(parameters, user_session)
    if intent == 'UserProvidesPages':
        response = userProvidesPages(parameters, user_session)
    if intent == 'UserProvidesPagesRelevance':
        response = userProvidesPagesRelevance(parameters, user_session)
    if intent == 'UserProvidesRate':
        response = userProvidesRate(parameters, user_session)
    if intent == 'UserProvidesRateRelevance':
        response = userProvidesRateRelevance(parameters, user_session)
    if intent == 'UserProvidesDate':
        response = userProvidesDate(parameters, user_session)
    if intent == 'UserProvidesDateRelevance':
        response = userProvidesDateRelevance(parameters, user_session)
    if intent == 'UserProvidesDateEmpty':
        response = userProvidesDateEmpty(user_session)
    if intent == 'skip':
        response = skip(user_session, outputContexts)


    
    return JsonResponse(response)



#TODO:
#Refactorizar
#unificar atributos: rate, rating y demas
#Que en el mensaje de similar author ponga también el autor al que es similar.

#No se puede controlar que el rating no salga de 1 a 5, y el pages relevance, porque entra en los otros contextos.HAy que sacar
#la forma de hacer set del contexto con fulfillment y que SOLO tenga ese contexto.


