from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class Person:
    id: uuid4
    full_name: str
    created: datetime
    modified: datetime
