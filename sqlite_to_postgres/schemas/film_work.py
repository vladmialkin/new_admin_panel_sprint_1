from dataclasses import dataclass
from datetime import date, datetime
from uuid import uuid4


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
