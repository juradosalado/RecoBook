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
    title = models.TextField(verbose_name='Título')
    series = models.TextField(verbose_name='Saga')
    authors = models.ManyToManyField(Author)
    average_rating = models.DecimalField(verbose_name="Puntuación media", decimal_places=2, max_digits=3)
    num_ratings = models.IntegerField(verbose_name="Número de puntuaciones")
    description = models.TextField(verbose_name='Sinopsis')
    language = models.TextField(verbose_name='Idioma')
    genres = models.ManyToManyField(Genre)
    pages_number = models.IntegerField(verbose_name='Número de páginas', null=True)
    publish_date = models.DateField(verbose_name='Fecha de publicación', null=True)
    setting = models.ManyToManyField(Setting)
    cover = models.URLField(verbose_name='Portada')

    def __str__(self):
        return self.title
