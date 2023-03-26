import datetime
from main.models import Author, Book, Genre, Setting, UserSession
from django.db.models import Q
from bs4 import BeautifulSoup
from urllib.request import urlopen


books = Book.objects.all()
dictScores = dict()
dictMatching = dict()

preferred_genres_by_age=dict()

preferred_genres_by_age['0-18']= Genre.objects.filter(Q(name__icontains='Graphic') |Q(name__icontains='Comic') | Q(name__icontains='Comedy') | Q(name__icontains='Humor') | Q(name__icontains="Fantasy") | Q(name__icontains='Science Fiction')| Q(name__icontains='Young Adult'))
preferred_genres_by_age['18-35']= Genre.objects.filter(Q(name__icontains='Mystery') | Q(name__icontains='Thriller') | Q(name__icontains='Crime') | Q(name__icontains='Romance') | Q(name__icontains="Fantasy") | Q(name__icontains='Science Fiction'))
preferred_genres_by_age['36-70+']= Genre.objects.filter(Q(name__icontains='Mystery') | Q(name__icontains='Thriller') | Q(name__icontains='Crime') | Q(name__icontains='Biography') | Q(name__icontains='History') | Q(name__icontains='Historical'))

def reset_scores(user_session):
    if user_session in dictScores:
        dictScores[user_session].clear()
    if user_session in dictMatching:
        dictMatching[user_session].clear()
        
def add_matching_text(element, book, matching_text, user_session):
    if isinstance(element, int) | isinstance(element,float) | isinstance(element,datetime.date):
        string_to_add= str(element)
    else:
        string_to_add=element.name
    if user_session in dictMatching:
        if book in dictMatching[user_session]:
            list = dictMatching[user_session][book]
            string = list[-1]
            if matching_text not in string:
                new_string=matching_text + string_to_add
                list.append(new_string)
            else:
                string+=", "+string_to_add
                list[-1]=string
        else:
            list = []
            string = matching_text + string_to_add
            list.append(string)
        dictMatching[user_session][book] = list
    else:
        dictMatching[user_session] = dict()
        list = []
        string = matching_text + string_to_add
        list.append(string)
        dictMatching[user_session][book] = list



def aux_add_age_score(user_session, book, age_relevance, matching_text, age_range):
    for genre in preferred_genres_by_age[age_range]:
                if genre in book.genres.all():
                    if user_session in dictScores:
                        if book in dictScores[user_session]:
                            dictScores[user_session][book] += age_relevance / len(preferred_genres_by_age[age_range])
                        else:
                            dictScores[user_session][book] = age_relevance / len(preferred_genres_by_age[age_range])
                    else:
                        dictScores[user_session] = dict()
                        dictScores[user_session][book] = age_relevance / len(preferred_genres_by_age[age_range])
                    add_matching_text(genre, book, matching_text, user_session)


def add_age_score(user_session):
    session_id = user_session.session_id
    age = user_session.age
    age_relevance = int(user_session.age_relevance)
    matching_text = "Most popular genres by readers of your age: "
    for book in books:
        if age <= 18:
            aux_add_age_score(user_session, book, age_relevance, matching_text, '0-18')
            #It tries not to recommend long books to young kids
            if age<=13 and book.pages_number>300:
                dictScores[user_session][book] -= age_relevance / 2

        elif age <= 35:
            aux_add_age_score(user_session, book, age_relevance, matching_text, '18-35')
        else:
            aux_add_age_score(user_session, book, age_relevance, matching_text, '36-70+')
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.is_waiting = False
    user_session.save()

def add_genres_score(user_session):
    session_id = user_session.session_id
    genres = user_session.genres.all()

    genres_relevance = int(user_session.genres_relevance)

    for book in books:
        for genre in genres:
            if genre in book.genres.all():
                if user_session in dictScores:
                    if book in dictScores[user_session]:
                        dictScores[user_session][book] += genres_relevance / len(genres)
                    else:
                        dictScores[user_session][book] = genres_relevance / len(genres)
                else:
                    dictScores[user_session] = dict()
                    dictScores[user_session][book] = genres_relevance / len(genres)
                matching_text= "Genres you were looking for: "
                add_matching_text(genre, book, matching_text, user_session)
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.is_waiting = False
    user_session.save()            

def add_author_score(user_session):
    session_id = user_session.session_id
    author_name = user_session.author_name
    #it will always find an author, because it wouldn't call the function if it doesn't
    author = Author.objects.get(name=author_name)
    author_relevance = int(user_session.author_relevance)

    for book in books:
        if author in book.authors.all():
            if user_session in dictScores:
                if book in dictScores[user_session]:
                    dictScores[user_session][book] += author_relevance
                else:
                    dictScores[user_session][book] = author_relevance
            else:
                dictScores[user_session] = dict()
                dictScores[user_session][book] = author_relevance
            matching_text= "Author you were looking for: "
            add_matching_text(author, book, matching_text, user_session)
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.is_waiting = False
    user_session.save()

def add_similar_authors_score(user_session):
    session_id = user_session.session_id
    authors = user_session.similar_authors.all()
    similar_authors_relevance = int(user_session.similar_authors_relevance)
    base_url = "https://www.literature-map.com/"
    all_similar_authors = []
    for author in authors:
        url = base_url+author.name.replace(' ','+')
        f = urlopen(url)
        s=BeautifulSoup(f, "html.parser")
        links=s.find("div", id="gnodMap").find_all("a")
        similar_authors_names = []
        i=1
        while i<11:
            similar_author = links[i].text
            similar_authors_names.append(similar_author)
            i+=1
        similar_authors = Author.objects.filter(name__in=similar_authors_names)
        all_similar_authors.append(similar_authors)
    for book in books:
        for similar_authors in all_similar_authors:
            for author in similar_authors:
                if author in book.authors.all():
                    if user_session in dictScores:
                        if book in dictScores[user_session]:
                            dictScores[user_session][book] += similar_authors_relevance / len(authors)
                        else:
                            dictScores[user_session][book] = similar_authors_relevance / len(authors)
                    else:
                        dictScores[user_session] = dict()
                        dictScores[user_session][book] = similar_authors_relevance / len(authors)
                    matching_text= "Similar authors to the ones you were looking for: "
                    add_matching_text(author, book, matching_text, user_session)
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.is_waiting = False
    user_session.save()

def add_settings_score(user_session):
    session_id = user_session.session_id
    settings = user_session.settings.all()
    settings_relevance = int(user_session.settings_relevance)
    for book in books:
        for setting in settings:
            if setting in book.setting.all():
                if user_session in dictScores:
                    if book in dictScores[user_session]:
                        dictScores[user_session][book] += settings_relevance
                    else:
                        dictScores[user_session][book] = settings_relevance
                else:
                    dictScores[user_session] = dict()
                    dictScores[user_session][book] = settings_relevance
                matching_text= "Settings you were looking for: "
                add_matching_text(setting, book, matching_text, user_session)
                #It will only check that one of your settings is in the book, so it doesn't count twice settings like:
                #'Ireland' and 'Dublin, Ireland'
                user_session = UserSession.objects.get(session_id=session_id)
                user_session.is_waiting = False
                user_session.save()
                break
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.is_waiting = False
    user_session.save()

def add_pages_number_score(user_session):
    session_id = user_session.session_id
    pages_number =  user_session.pages_number
    pages_number_relevance = int(user_session.pages_number_relevance)
    for book in books:
        if book.pages_number is not None:
            if book.pages_number <= pages_number:
                if user_session in dictScores:
                    if book in dictScores[user_session]:
                        dictScores[user_session][book] += pages_number_relevance
                    else:
                        dictScores[user_session][book] = pages_number_relevance
                else:
                    dictScores[user_session] = dict()
                    dictScores[user_session][book] = pages_number_relevance
                matching_text = "Number of pages you were looking for: "
                add_matching_text(book.pages_number, book, matching_text, user_session)
            else:
                if user_session in dictScores:
                    if book in dictScores[user_session]:
                        #if relevance is 10 and the books have 100 pages more than user wanted, it will add nothing
                        dictScores[user_session][book] += pages_number_relevance - (book.pages_number - pages_number) * 0.01*pages_number_relevance
                    else:
                        dictScores[user_session][book] = pages_number_relevance - (book.pages_number - pages_number) * 0.01*pages_number_relevance
                else:
                    dictScores[user_session] = dict()
                    dictScores[user_session][book] = pages_number_relevance - (book.pages_number - pages_number) * 0.01*pages_number_relevance
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.is_waiting = False
    user_session.save()

def add_rating_score(user_session):
    session_id = user_session.session_id
    rating = user_session.rating
    rating_relevance = int(user_session.rating_relevance)
    for book in books:
        if book.average_rating is not None:
            if book.average_rating >= rating:
                if user_session in dictScores:
                    if book in dictScores[user_session]:
                        dictScores[user_session][book] += rating_relevance
                    else:
                        dictScores[user_session][book] = rating_relevance
                else:
                    dictScores[user_session] = dict()
                    dictScores[user_session][book] = rating_relevance
                matching_text = "Rating you were looking for: "
                add_matching_text(float(book.average_rating), book, matching_text, user_session)
            else:
                if user_session in dictScores:
                    if book in dictScores:
                        #if relevance = 10 and the book has 1 point less than user wanted, it will add nothing
                        dictScores[user_session][book] += rating_relevance - (rating - float(book.average_rating)) *1*rating_relevance
                    else:
                        dictScores[user_session][book] = rating_relevance - (rating - float(book.average_rating)) *1*rating_relevance
                else:
                    dictScores[user_session] = dict()
                    dictScores[user_session][book] = rating_relevance - (rating - float(book.average_rating)) *1*rating_relevance
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.is_waiting = False
    user_session.save()


def add_date_score(user_session):
    session_id = user_session.session_id
    date_after = user_session.date_after
    date_before = user_session.date_before
    date_relevance = int(user_session.date_relevance)
    for book in books:
        if book.publish_date is not None:
            if book.publish_date >= date_after:
                if book.publish_date <= date_before:
                    if user_session in dictScores:
                        if book in dictScores[user_session]:
                            dictScores[user_session][book] += date_relevance
                        else:
                            dictScores[user_session][book] = date_relevance
                    else:
                        dictScores[user_session] = dict()
                        dictScores[user_session][book] = date_relevance
                    matching_text = "Published between the dates you stablished: "
                    add_matching_text(book.publish_date, book, matching_text, user_session)
                else:
                    if user_session in dictScores:
                        if book in dictScores[user_session]:
                            #if relevance is 3 and it was published 3 years later, it will add nothing
                            dictScores[user_session][book] += date_relevance - ((book.publish_date -date_before).days / 365 *3)* date_relevance
                        else:
                            dictScores[user_session][book] = date_relevance - ((book.publish_date -date_before).days / 365 *3)* date_relevance
                    else:
                        dictScores[user_session] = dict()
                        dictScores[user_session][book] = date_relevance - ((book.publish_date -date_before).days / 365 *3)* date_relevance
            else:
                if user_session in dictScores:
                    if book in dictScores[user_session]:
                        dictScores[user_session][book] +=  date_relevance - ((date_before-book.publish_date ).days / 365 *3)* date_relevance
                    else:
                        dictScores[user_session][book] = date_relevance - ((date_before-book.publish_date ).days / 365 *3)* date_relevance
                else:
                    dictScores[user_session] = dict()
                    dictScores[user_session][book] = date_relevance - ((date_before-book.publish_date ).days / 365 *3)* date_relevance
    user_session = UserSession.objects.get(session_id=session_id)
    user_session.is_waiting = False
    user_session.save()