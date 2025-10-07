from typing import Optional
from pydantic import BaseModel

class Timestamp(BaseModel):
    """Represents a \"fuzzy date\" from the API. Each part of the date may be missing."""
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]
