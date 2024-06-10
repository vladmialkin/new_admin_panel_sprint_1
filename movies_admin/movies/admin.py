from django.contrib import admin

from .models import Genre, FilmWork, GenreFilmWork, Person, PersonFilmWork


# Register your models here.
class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork

class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)

    list_display = ('title', 'type', 'creation_date', 'rating',)

    list_filter = ('type','creation_date')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass
