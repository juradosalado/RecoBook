import datetime
from main.models import Author, Book, Genre, Setting
from django.db.models import Q
from bs4 import BeautifulSoup
from urllib.request import urlopen


books = Book.objects.all()
dictScores = dict()
dictMatching = dict()

preferred_genres_by_age=dict()

preferred_genres_by_age['0-18']= Genre.objects.filter(Q(name__icontains='Graphic') |Q(name__icontains='Comic') | Q(name__icontains='Comedy') | Q(name__icontains='Humor') | Q(name__icontains="Fantasy") | Q(name__icontains='Science Fiction')| Q(name__icontains='Young Adult'))
#preferred_genres_by_age['18-35']= Genre.objects.filter(Q(name__icontains='Mystery'))
preferred_genres_by_age['18-35']= Genre.objects.filter(Q(name__icontains='Mystery') | Q(name__icontains='Thriller') | Q(name__icontains='Crime') | Q(name__icontains='Romance') | Q(name__icontains="Fantasy") | Q(name__icontains='Science Fiction'))
preferred_genres_by_age['36-70+']= Genre.objects.filter(Q(name__icontains='Mystery') | Q(name__icontains='Thriller') | Q(name__icontains='Crime') | Q(name__icontains='Biography') | Q(name__icontains='History') | Q(name__icontains='Historical'))
def reset_scores():
    dictScores.clear()
    dictMatching.clear()

def add_matching_text(element, book, matching_text):
    if isinstance(element, int) | isinstance(element,float) | isinstance(element,datetime.date):
        string_to_add= str(element)
    else:
        string_to_add=element.name
    if book in dictMatching:
        list = dictMatching[book]
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
    dictMatching[book] = list






def add_age_score(age, age_relevance):
    matching_text = "Most popular genres by readers of your age: "
    for book in books:
        if age <= 18:
            for genre in preferred_genres_by_age['0-18']:
                if genre in book.genres.all():
                    if book in dictScores:
                        dictScores[book] += age_relevance / (preferred_genres_by_age['0-18'].count())
                    else:
                        dictScores[book] = age_relevance / (preferred_genres_by_age['0-18'].count())
                    add_matching_text(genre, book, matching_text)
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
                        dictScores[book] += age_relevance / (preferred_genres_by_age['18-35'].count())
                    else:
                        dictScores[book] = age_relevance / (preferred_genres_by_age['18-35'].count())
                    add_matching_text(genre, book, matching_text)
        else:
            for genre in preferred_genres_by_age['36-70+']:
                if genre in book.genres.all():
                    if book in dictScores:
                        dictScores[book] += age_relevance / (preferred_genres_by_age['36-70+'].count())
                    else:
                        dictScores[book] = age_relevance / (preferred_genres_by_age['36-70+'].count())
                    add_matching_text(genre, book, matching_text)

def add_genres_score(genres, genres_relevance):
    for book in books:
        for genre in genres:
            if genre in book.genres.all():
                if book in dictScores:
                    dictScores[book] += genres_relevance / genres.count()
                else:
                    dictScores[book] = genres_relevance / genres.count()
                add_matching_text(genre, book, matching_text= "Genres you were looking for: ")
                

def add_author_score(author, author_relevance):
    for book in books:
        if author in book.authors.all():
            if book in dictScores:
                dictScores[book] += author_relevance
            else:
                dictScores[book] = author_relevance
            add_matching_text(author, book, matching_text= "Author you were looking for: ")

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
                if author in book.authors.all():
                    if book in dictScores:
                        dictScores[book] += similar_authors_relevance / authors.count()
                    else:
                        dictScores[book] = similar_authors_relevance / authors.count()
                    add_matching_text(author, book, matching_text= "Similar authors to the ones you were looking for: ")

def add_setting_score(settings, setting_relevance):
    for book in books:
        for setting in settings:
            if setting in book.setting.all():
                if book in dictScores:
                    dictScores[book] += setting_relevance
                else:
                    dictScores[book] = setting_relevance
                add_matching_text(setting, book, matching_text= "Setting you were looking for: ")
                #It will only check that one of your settings is in the book, so it doesn't count twice settings like:
                #'Ireland' and 'Dublin, Ireland'
                break

def add_pages_number_score(pages_number, pages_number_relevance):
    for book in books:
        if book.pages_number is not None:
            if book.pages_number <= pages_number:
                if book in dictScores:
                    dictScores[book] += pages_number_relevance
                else:
                    dictScores[book] = pages_number_relevance
                add_matching_text(book.pages_number, book, matching_text= "Number of pages you were looking for: ")
            else:
                if book in dictScores:
                    dictScores[book] -= (book.pages_number - pages_number) * pages_number_relevance /300
                else:
                    dictScores[book] = -(book.pages_number - pages_number) * pages_number_relevance /300

def add_date_before_score(date, date_before_relevance):
    for book in books:
        if book.publish_date is not None:
            if book.publish_date <= date:
                if book in dictScores:
                    dictScores[book] += date_before_relevance
                else:
                    dictScores[book] = date_before_relevance
                add_matching_text(book.publish_date, book, matching_text= "Published after the date you stablished: ")
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
                add_matching_text(book.publish_date, book, matching_text= "Published after the date you stablished: ")
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
                add_matching_text(float(book.average_rating), book, matching_text= "Rating you were looking for: ")
            else:
                if book in dictScores:
                    dictScores[book] -= (rating - float(book.average_rating)) * rating_relevance
                else:
                    dictScores[book] = -(rating - float(book.average_rating)) * rating_relevance


