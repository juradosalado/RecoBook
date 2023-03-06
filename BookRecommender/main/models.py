from django.db import models

# Create your models here.
class Author(models.Model):
    author_id = models.IntegerField(primary_key=True)
    name = models.TextField(verbose_name='Autor')

    def __str__(self):
        return self.name

class Genre(models.Model):
    genre_id = models.IntegerField(primary_key=True)
    name = models.TextField(verbose_name='Género')

    def __str__(self):
        return self.name

class Setting(models.Model):
    setting_id = models.IntegerField(primary_key=True)
    name = models.TextField(verbose_name='Ambientación')

    def __str__(self):
        return self.name

class Book(models.Model):
    book_id = models.IntegerField(primary_key=True)
    title = models.TextField(verbose_name='Títulos')
    authors = models.ManyToManyField(Author)
    average_rating = models.DecimalField(verbose_name="Puntuación media", decimal_places=2, max_digits=3)
    num_ratings = models.IntegerField(verbose_name="Número de puntuaciones")
    description = models.TextField(verbose_name='Sinopsis')
    genres = models.ManyToManyField(Genre)
    pages_number = models.IntegerField(verbose_name='Número de páginas', null=True)
    publish_date = models.DateField(verbose_name='Fecha de publicación', null=True)
    setting = models.ManyToManyField(Setting)
    cover = models.URLField(verbose_name='Portada')

    def __str__(self):
        return self.title
    
class UserSession(models.Model):
    session_id = models.CharField(max_length=320, primary_key=True)
    name = models.TextField(verbose_name='Nombre', null=True)
    age = models.IntegerField(verbose_name='Edad', null=True)
    age_relevance = models.IntegerField(verbose_name='Relevancia de la edad',null=True)
    genres = models.ManyToManyField(Genre,null=True)
    genres_relevance = models.IntegerField(null=True)
    author_name = models.TextField(null=True)
    author_relevance = models.IntegerField(verbose_name='Relevancia del autor',null=True)
    similar_authors = models.ManyToManyField(Author, null=True)
    similar_authors_relevance = models.IntegerField(verbose_name='Relevancia de los autores similares', null=True)
    settings = models.ManyToManyField(Setting, null=True)
    settings_relevance = models.IntegerField(verbose_name='Relevancia de la ambientación', null=True)
    pages_number = models.IntegerField(verbose_name='Número de páginas', null=True)
    pages_number_relevance = models.IntegerField(verbose_name='Relevancia del número de páginas', null=True)
    rating = models.IntegerField(verbose_name="Nota media", null=True)
    rating_relevance = models.IntegerField(verbose_name='Relevancia de la nota media', null=True)
    date_before = models.DateField(verbose_name="Fecha anterior", null=True)
    date_after = models.DateField(verbose_name="Fecha posterior",null=True)
    date_relevance = models.IntegerField(verbose_name='Relevancia de la fecha', null=True)
    is_waiting = models.BooleanField(default=False)



    def __str__(self):
        return self.session_id
