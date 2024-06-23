from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class GenreFilmWork:
    id: uuid4
    film_work_id: uuid4
    genre_id: uuid4
    created: datetime
