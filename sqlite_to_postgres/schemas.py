from dataclasses import dataclass, field
from datetime import datetime, date
from uuid import uuid4, UUID


@dataclass
class Person:
    id: uuid4
    full_name: str
    created: datetime
    modified: datetime


@dataclass
class Genre:
    id: uuid4
    name: str
    description: str
    created: datetime
    modified: datetime


@dataclass
class GenreFilmWork:
    id: uuid4
    genre_id: uuid4
    film_work_id: uuid4
    created: datetime

@dataclass
class PersonFilmWork:
    id: uuid4
    person_id: uuid4
    film_work_id: uuid4
    role: str
    created: datetime


@dataclass
class FilmWork:
    id: uuid4
    title: str
    description: str
    creation_date: date
    file_path: str
    rating: float
    type: str
    created: datetime
    modified: datetime
