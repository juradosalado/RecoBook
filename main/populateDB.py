import ast
import csv
from datetime import datetime
import re
from main.models import Author, Book, Genre, Setting


def populate():
    (b, g, s, a)=populateBooks()
    load_similar_books()
    return (b,g,s, a)

def add_many_to_many(item_id, list_of_items, items_set, cls):
    items = []
    for item in list_of_items:
        if item.strip() not in items_set:
            items_set.add(item.strip())
            itemToAdd=cls(item_id, item.strip())
            itemToAdd.save()
            item_id +=1
        else:
            print(item.strip())
            itemToAdd=cls.objects.filter(name=item.strip()).first()
        items.append(itemToAdd)
    return items, item_id

def populateBooks():
    Book.objects.all().delete()
    Genre.objects.all().delete()
    Setting.objects.all().delete()
    Author.objects.all().delete()

    genres_set = set()
    genre_id = 0

    settings_set = set()
    setting_id = 0

    authors_set = set()
    author_id = 0
    try:
        with open("data\\books.csv", 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            book_id=0
            for row in reader:
                if book_id<1000:
                    title = row[1].strip()
                    series = row[2].strip()
                    #Do not store books that are not first in a series. It has no sense to recommend them
                    if "#" in series and "#1" not in series:
                        continue
                    average_rating = float(row[4].strip())
                    num_ratings = int(row[17])
                    description = row[5].strip()
                    language = row[6].strip()
                    pages_number = None if len(row[12].strip()) == 0 else int(row[12].strip())
                    publish_date = None if len(row[15].strip()) == 0 else datetime.strptime(row[15].strip(), '%m/%d/%y')
                    cover = row[21].strip()

                    book=Book(book_id=book_id, title=title, average_rating=average_rating, num_ratings=num_ratings,description=description, pages_number=pages_number, publish_date=publish_date, cover=cover)
                    book.save()

                    list_of_authors = row[3].strip().split(',')
                    list_of_authors = [re.sub(r"\(.*?\)", "", author.strip()) for author in list_of_authors]
                    authors, author_id = add_many_to_many(author_id, list_of_authors, authors_set, Author)
                    book.authors.set(authors)

                    list_of_genres = ast.literal_eval(row[8].strip())
                    genres, genre_id = add_many_to_many(genre_id, list_of_genres, genres_set, Genre)
                    book.genres.set(genres)

                    list_of_settings = ast.literal_eval(row[20].strip())
                    settings, setting_id = add_many_to_many(setting_id, list_of_settings, settings_set, Setting)
                    book.setting.set(settings)

                    book.save()
                    book_id+=1
            return (Book.objects.count(), Genre.objects.count(), Setting.objects.count(), Author.objects.count())

    except FileNotFoundError:
        print("File does not exist")
        return (0,0,0)

def load_similar_books():
    #don't know if it will be efficient to calculate similarities between books
    pass

