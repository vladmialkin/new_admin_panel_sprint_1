from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class PersonFilmWork:
    id: uuid4
    film_work_id: uuid4
    person_id: uuid4
    role: str
    created: datetime
