import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class CustomTypeField(models.TextChoices):
    MOVIE = ("MV", _('movie'))
    TV_SHOW = ("TV", _('tv_show'))


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
    name = models.CharField(verbose_name=_('name'), max_length=255)
    description = models.TextField(verbose_name=_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class FilmWork(UUIDMixin, TimeStampedMixin):
    title = models.TextField(verbose_name=_('title'))
    description = models.TextField(verbose_name=_('description'), blank=True, null=True)
    creation_date = models.DateField(verbose_name=_('creation_date'), blank=True, null=True)
    rating = models.FloatField(verbose_name=_('rating'), blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField(
        verbose_name=_('type'),
        max_length=2,
        choices=CustomTypeField.choices,
        default=CustomTypeField.MOVIE,
    )
    genres = models.ManyToManyField(Genre, through='GenreFilmWork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Film work')
        verbose_name_plural = _('Films')

    def __str__(self):
        return self.title


class GenreFilmWork(UUIDMixin):
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('Genre film work')
        verbose_name_plural = _('Genres films')

    def __str__(self):
        return f"{_('Genre')}: {self.genre} {_('Film work')}: {self.film_work}"


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(verbose_name=_('full_name'), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


class PersonFilmWork(UUIDMixin):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    role = models.TextField(verbose_name=_('role'))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('Person film work')
        verbose_name_plural = _('Persons films')

    def __str__(self):
        return f"{_('Person')}: {self.person} {_('Film work')}: {self.film_work}"