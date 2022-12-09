import ast
import csv
from datetime import datetime
from main.models import Book, Genre, Setting


def populate():
    (b, g, s)=populateBooks()
    return (b,g,s)



def populateBooks():
    Book.objects.all().delete()
    Genre.objects.all().delete()
    Setting.objects.all().delete()

    genres_set = set()
    genre_id = 0
    print(genres_set)
    settings_set = set()
    setting_id = 0
    try:
        with open("data\\books.csv", 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            i=0
            for row in reader:
                if i<100:
                    isbn = row[7].strip()
                    title = row[1].strip()
                    series = row[2].strip()
                    #TODO: Don't store books that are not first in a series
                    author = row[3].strip()
                    average_rating = float(row[4].strip())
                    num_ratings = int(row[17])
                    description = row[5].strip()
                    language = row[6].strip()
                    pages_number = int(row[12].strip())
                    publish_date = None if len(row[15].strip()) == 0 else datetime.strptime(row[15].strip(), '%m/%d/%y')
                    cover = row[21].strip()


                    book=Book(isbn=isbn, title=title, series=series, author=author, average_rating=average_rating, num_ratings=num_ratings,description=description, language=language, pages_number=pages_number, publish_date=publish_date, cover=cover)
                    book.save()
                    print(book)
                    list_of_genres = ast.literal_eval(row[8].strip())
                    genres = []
                    for genre in list_of_genres:
                        if genre not in genres_set:
                            genres_set.add(genre)
                            genre=Genre(genre_id=genre_id, name=genre)
                            genre.save()
                            genre_id +=1
                        else:
                            genre=Genre.objects.get(name=genre)
                        genres.append(genre)
                    book.genres.set(genres)

                    list_of_settings = ast.literal_eval(row[20].strip())
                    settings = []
                    for setting in list_of_settings:
                        if setting not in settings_set:
                            settings_set.add(setting)
                            setting=Setting(setting_id=setting_id, name=setting)
                            setting.save()
                            setting_id +=1
                        else:
                            setting=Setting.objects.get(name=setting)
                        settings.append(setting)
                    book.setting.set(settings)
                    book.save()
                    i+=1
            #print books with languages NOT in English
            print(Book.objects.filter(language="English").count())
            return (Book.objects.count(), Genre.objects.count(), Setting.objects.count())

    except FileNotFoundError:
        print("El archivo no existe")
        return (0,0,0)
