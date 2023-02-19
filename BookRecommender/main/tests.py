from django.test import TestCase

from main.models import *
from main.RS import *
# Create your tests here.

class RecommendationSystemTestCase(TestCase):
    def setUp(self):
        Author.objects.create(
            author_id=1,
            name="Jon Denbrough",
        )
        Author.objects.create(
            author_id=2,
            name="Brandon Sanderson",
        )

        Author.objects.create(
            author_id=3,
            name="Pierce Brown",
        )
        Setting.objects.create(
            setting_id=1,
            name="Maastricht",
        )
        Setting.objects.create(
            setting_id=2,
            name="Roshar",
        )
        Genre.objects.create(
            genre_id=1,
            name="Mystery",
        )
        Genre.objects.create(
            genre_id=2,
            name="Historical",
        )
        Book.objects.create(
            book_id=1,
            title="In another life",
            average_rating=4.5,
            num_ratings=100,
            pages_number=200,
            publish_date="2013-01-28",
        )
        Book.objects.create(
            book_id=2,
            title="The way of kings",
            average_rating=2.5,
            num_ratings=100,
            pages_number=600,
            publish_date="1977-01-28",
        )

        Book.objects.get(book_id=1).authors.add(Author.objects.get(author_id=1))
        Book.objects.get(book_id=2).authors.add(Author.objects.get(author_id=2))
        Book.objects.get(book_id=1).setting.add(Setting.objects.get(setting_id=1))
        Book.objects.get(book_id=2).setting.add(Setting.objects.get(setting_id=2))
        Book.objects.get(book_id=1).genres.add(Genre.objects.get(genre_id=1))
        Book.objects.get(book_id=2).genres.add(Genre.objects.get(genre_id=2))

    book_1 = Book.objects.get(book_id=1)
    book_2 = Book.objects.get(book_id=2)
    list_of_books = [book_1, book_2]

    def test_age(self):
        reset_scores()
        add_age_score(20, 4)
        for book in self.list_of_books:
            if book not in dictScores:
                dictScores[book] = 0
        self.assertTrue(dictScores[self.book_1]>dictScores[self.book_2])

    def test_genres(self):
        reset_scores()
        genres = Genre.objects.filter(Q(name='Mystery'))
        add_genres_score(genres, 10)
        for book in self.list_of_books:
            if book not in dictScores:
                dictScores[book] = 0
        self.assertTrue(dictScores[self.book_1]>dictScores[self.book_2])
    
    def test_author(self):
        reset_scores()
        author = Author.objects.get(name='Jon Denbrough')
        add_author_score(author, 2)
        for book in self.list_of_books:
            if book not in dictScores:
                dictScores[book] = 0
        self.assertTrue(dictScores[self.book_1]>dictScores[self.book_2])
    
    def test_similar_author(self):
        reset_scores()
        author = Author.objects.get(name='Pierce Brown')
        authors = [author]
        add_similar_authors_score(authors, 2)
        for book in self.list_of_books:
            if book not in dictScores:
                dictScores[book] = 0
        self.assertTrue(dictScores[self.book_1]<dictScores[self.book_2])


    def test_setting(self):
        reset_scores()
        setting = Setting.objects.filter(Q(name__icontains='Maastricht'))
        add_setting_score(setting, 2)
        for book in self.list_of_books:
            if book not in dictScores:
                dictScores[book] = 0
        self.assertTrue(dictScores[self.book_1]>dictScores[self.book_2])
    
    def test_pages_number(self):
        reset_scores()
        add_pages_number_score(500, 2)
        for book in self.list_of_books:
            if book not in dictScores:
                dictScores[book] = 0
        self.assertTrue(dictScores[self.book_1]>dictScores[self.book_2])
    
    def test_publish_date(self):
        reset_scores()
        date_after = datetime.date(2010, 4, 7)
        date_before = datetime.date(2015, 4, 7)
        add_date_score(date_after, date_before, 2)
        for book in self.list_of_books:
            if book not in dictScores:
                dictScores[book] = 0
        self.assertTrue(dictScores[self.book_1]>dictScores[self.book_2])

    def test_rating(self):
        reset_scores()
        add_rating_score(4, 3)
        for book in self.list_of_books:
            if book not in dictScores:
                dictScores[book] = 0
        self.assertTrue(dictScores[self.book_1]>dictScores[self.book_2])



