import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class CustomTypeField(models.TextChoices):
    MOVIE = ("MV", "movie")
    TV_SHOW = ("TV", "tv_show")


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(verbose_name='name', max_length=255)
    description = models.TextField(verbose_name='description', blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.id


class FilmWork(UUIDMixin, TimeStampedMixin):
    title = models.TextField(verbose_name='title')
    description = models.TextField(verbose_name='description', blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField(
        max_length=2,
        choices=CustomTypeField.choices,
        default=CustomTypeField.MOVIE,
    )
    genres = models.ManyToManyField(Genre, through='GenreFilmWork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'

    def __str__(self):
        return self.title


class GenreFilmWork(UUIDMixin):
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = 'Жанр кинопроизведения'
        verbose_name_plural = 'Жанры кинопроизведения'

    def __str__(self):
        return f"Жанр: {self.genre} Кинопроизведение: {self.film_work}"


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(verbose_name='full_name', max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = 'Персонаж'
        verbose_name_plural = 'Персонажи'

    def __str__(self):
        return self.full_name


class PersonFilmWork(UUIDMixin):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    role = models.TextField(verbose_name='role')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = 'Персонаж кинопроизведения'
        verbose_name_plural = 'Персонажи кинопроизведения'

    def __str__(self):
        return f"Персонаж: {self.person} Кинопроизведение: {self.film_work}"