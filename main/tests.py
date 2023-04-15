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

        UserSession.objects.create(
            session_id="1",
            name="Jon",
            age=20,
            age_relevance=4,
            genres_relevance=10,
            author_name = "Jon Denbrough",
            author_relevance = 2,
            similar_authors_relevance = 2,
            settings_relevance = 2,
            pages_number = 500,
            pages_number_relevance = 2,
            rating = 4,
            rating_relevance = 3,
            date_after = datetime.date(2010, 4, 7),
            date_before = datetime.date(2015, 4, 7),
            date_relevance = 2
        )
        Book.objects.get(book_id=1).authors.add(Author.objects.get(author_id=1))
        Book.objects.get(book_id=2).authors.add(Author.objects.get(author_id=2))
        Book.objects.get(book_id=1).setting.add(Setting.objects.get(setting_id=1))
        Book.objects.get(book_id=2).setting.add(Setting.objects.get(setting_id=2))
        Book.objects.get(book_id=1).genres.add(Genre.objects.get(genre_id=1))
        Book.objects.get(book_id=2).genres.add(Genre.objects.get(genre_id=2))
        UserSession.objects.get(session_id="1").genres.add(Genre.objects.get(genre_id=1))
        UserSession.objects.get(session_id="1").similar_authors.add(Author.objects.get(author_id=3))
        UserSession.objects.get(session_id="1").settings.add(Setting.objects.get(setting_id=1))

    def test_age(self):
        book_1 = Book.objects.get(book_id=1)
        book_2 = Book.objects.get(book_id=2)
        user_session = UserSession.objects.get(session_id="1")
        
        list_of_books = [book_1, book_2]
        reset_scores(user_session)
        add_age_score(user_session)
        for book in list_of_books:
            if book not in dictScores[user_session]:
                dictScores[user_session][book] = 0
        self.assertTrue(dictScores[user_session][book_1]>dictScores[user_session][book_2])

    def test_genres(self):
        book_1 = Book.objects.get(book_id=1)
        book_2 = Book.objects.get(book_id=2)
        user_session = UserSession.objects.get(session_id="1")
        list_of_books = [book_1, book_2]
        reset_scores(user_session)
        add_genres_score(user_session)
        for book in list_of_books:
            if book not in dictScores[user_session]:
                dictScores[user_session][book] = 0
        self.assertTrue(dictScores[user_session][book_1]>dictScores[user_session][book_2])
    
    def test_author(self):
        book_1 = Book.objects.get(book_id=1)
        book_2 = Book.objects.get(book_id=2)
        user_session = UserSession.objects.get(session_id="1")
        list_of_books = [book_1, book_2]
        reset_scores(user_session)
        add_author_score(user_session)
        for book in list_of_books:
            if book not in dictScores[user_session]:
                dictScores[user_session][book] = 0
        self.assertTrue(dictScores[user_session][book_1]>dictScores[user_session][book_2])
    
    def test_similar_author(self):
        book_1 = Book.objects.get(book_id=1)
        book_2 = Book.objects.get(book_id=2)
        user_session = UserSession.objects.get(session_id="1")
        list_of_books = [book_1, book_2]
        reset_scores(user_session)
        add_similar_authors_score(user_session)
        for book in list_of_books:
            if book not in dictScores[user_session]:
                dictScores[user_session][book] = 0
        self.assertTrue(dictScores[user_session][book_1]<dictScores[user_session][book_2])


    def test_setting(self):
        book_1 = Book.objects.get(book_id=1)
        book_2 = Book.objects.get(book_id=2)
        user_session = UserSession.objects.get(session_id="1")
        list_of_books = [book_1, book_2]
        reset_scores(user_session)
        add_settings_score(user_session)
        for book in list_of_books:
            if book not in dictScores[user_session]:
                dictScores[user_session][book] = 0
        self.assertTrue(dictScores[user_session][book_1]>dictScores[user_session][book_2])
    
    def test_pages_number(self):
        book_1 = Book.objects.get(book_id=1)
        book_2 = Book.objects.get(book_id=2)
        user_session = UserSession.objects.get(session_id="1")
        list_of_books = [book_1, book_2]
        reset_scores(user_session)
        add_pages_number_score(user_session)
        for book in list_of_books:
            if book not in dictScores[user_session]:
                dictScores[user_session][book] = 0
        self.assertTrue(dictScores[user_session][book_1]>dictScores[user_session][book_2])
    
    def test_publish_date(self):
        book_1 = Book.objects.get(book_id=1)
        book_2 = Book.objects.get(book_id=2)
        user_session = UserSession.objects.get(session_id="1")
        list_of_books = [book_1, book_2]
        reset_scores(user_session)
        add_date_score(user_session)
        for book in list_of_books:
            if book not in dictScores[user_session]:
                dictScores[user_session][book] = 0
        self.assertTrue(dictScores[user_session][book_1]>dictScores[user_session][book_2])

    def test_rating(self):
        book_1 = Book.objects.get(book_id=1)
        book_2 = Book.objects.get(book_id=2)
        user_session = UserSession.objects.get(session_id="1")
        list_of_books = [book_1, book_2]
        reset_scores(user_session)
        add_rating_score(user_session)
        for book in list_of_books:
            if book not in dictScores[user_session]:
                dictScores[user_session][book] = 0
        self.assertTrue(dictScores[user_session][book_1]>dictScores[user_session][book_2])


