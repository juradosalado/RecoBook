from main.models import Author, Book, Genre, Setting
from django.db.models import Q
from bs4 import BeautifulSoup
from urllib.request import urlopen


books = Book.objects.all()
dictScores = dict()
MATCHES_STRING = ""

preferred_genres_by_age=dict()

preferred_genres_by_age['0-18']= Genre.objects.filter(Q(name__icontains='Graphic') |Q(name__icontains='Comic') | Q(name__icontains='Comedy') | Q(name__icontains='Humor') | Q(name__icontains="Fantasy") | Q(name__icontains='Science Fiction'))
preferred_genres_by_age['18-35']= Genre.objects.filter(Q(name__icontains='Mystery') | Q(name__icontains='Thriller') | Q(name__icontains='Crime') | Q(name__icontains='Romance') | Q(name__icontains="Fantasy") | Q(name__icontains='Science Fiction'))
preferred_genres_by_age['36-70+']= Genre.objects.filter(Q(name__icontains='Mystery') | Q(name__icontains='Thriller') | Q(name__icontains='Crime') | Q(name__icontains='Biography') | Q(name__icontains='History') | Q(name__icontains='Historical'))
def reset_scores():
    dictScores.clear()
    MATCHES_STRING =""



def add_age_score(age, age_relevance):
    for book in books:
        if age <= 18:
            for genre in preferred_genres_by_age['0-18']:
                print("Este es el género"+genre)
                if genre in book.genres.all():
                    if book in dictScores:
                        dictScores[book] += age_relevance / (len(preferred_genres_by_age['0-18'])*0.6)
                    else:
                        dictScores[book] = age_relevance / (len(preferred_genres_by_age['0-18'])*0.6)
                        if "Most popular genres by readers of your age: " not in MATCHES_STRING:
                            MATCHES_STRING+="Most popular genres by readers of your age: " + genre.name
                        else:
                            MATCHES_STRING+=", "+genre.name
            #It tries not to recommend long books to young kids
            if age<=13 and book.pages_number>300:
                if book in dictScores:
                    dictScores[book] -= age_relevance / 2
                else:
                    dictScores[book] = -age_relevance / 2

        elif age <= 35:
            for genre in preferred_genres_by_age['18-35']:
                if genre in book.genres.all():
                    if book in dictScores:
                        dictScores[book] += age_relevance / (len(preferred_genres_by_age['18-35'])*0.6)
                    else:
                        dictScores[book] = age_relevance / (len(preferred_genres_by_age['18-35'])*0.6)
        else:
            for genre in preferred_genres_by_age['36-70+']:
                if genre in book.genres.all():
                    if book in dictScores:
                        dictScores[book] += age_relevance / (len(preferred_genres_by_age['36-70+'])*0.6)
                    else:
                        dictScores[book] = age_relevance / (len(preferred_genres_by_age['36-70+'])*0.6)

def add_genres_score(genres, genres_relevance):
    for book in books:
        for genre in genres:
            if genre in book.genres.all():
                if book in dictScores:
                    dictScores[book] += genres_relevance / (len(genres)*0.6)
                else:
                    dictScores[book] = genres_relevance / (len(genres)*0.6)

def add_author_score(author, author_relevance):
    for book in books:
        if author in book.author.all():
            if book in dictScores:
                dictScores[book] += author_relevance
            else:
                dictScores[book] = author_relevance

def add_similar_authors_score(authors, similar_authors_relevance):
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
                if author in book.author.all():
                    if book in dictScores:
                        dictScores[book] += similar_authors_relevance
                    else:
                        dictScores[book] = similar_authors_relevance

def add_setting_score(settings, setting_relevance):
    for book in books:
        for setting in settings:
            if setting in book.setting.all():
                if book in dictScores:
                    dictScores[book] += setting_relevance
                else:
                    dictScores[book] = setting_relevance

def add_pages_number_score(pages_number, pages_number_relevance):
    for book in books:
        if book.pages_number is not None:
            if book.pages_number <= pages_number:
                if book in dictScores:
                    dictScores[book] += pages_number_relevance
                else:
                    dictScores[book] = pages_number_relevance
            else:
                if book in dictScores:
                    dictScores[book] -= (book.pages_number - pages_number) * pages_number_relevance /100
                else:
                    dictScores[book] = -(book.pages_number - pages_number) * pages_number_relevance /100

def add_date_before_score(date, date_before_relevance):
    for book in books:
        if book.publish_date is not None:
            if book.publish_date <= date:
                if book in dictScores:
                    dictScores[book] += date_before_relevance
                else:
                    dictScores[book] = date_before_relevance
            else:
                if book in dictScores:
                    dictScores[book] -= (book.publish_date - date).days * date_before_relevance / 365*3
                else:
                    dictScores[book] = -(book.publish_date - date).days * date_before_relevance / 365*3

def add_date_after_score(date, date_after_relevance):
    for book in books:
        if book.publish_date is not None:
            if book.publish_date >= date:
                if book in dictScores:
                    dictScores[book] += date_after_relevance
                else:
                    dictScores[book] = date_after_relevance
            else:
                if book in dictScores:
                    dictScores[book] -= (date - book.publish_date).days * date_after_relevance / 365*3
                else:
                    dictScores[book] = -(date - book.publish_date).days * date_after_relevance / 365*3

def add_rating_score(rating, rating_relevance):
    for book in books:
        if book.average_rating is not None:
            if book.average_rating >= rating:
                if book in dictScores:
                    dictScores[book] += rating_relevance
                else:
                    dictScores[book] = rating_relevance
            else:
                if book in dictScores:
                    dictScores[book] -= (rating - float(book.average_rating)) * rating_relevance
                else:
                    dictScores[book] = -(rating - float(book.average_rating)) * rating_relevance


