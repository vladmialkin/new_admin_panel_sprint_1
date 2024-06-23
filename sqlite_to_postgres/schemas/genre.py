from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class Genre:
    id: uuid4
    name: str
    description: str
    created: datetime
    modified: datetime
