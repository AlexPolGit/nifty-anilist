from typing import Optional
from pydantic import BaseModel

class MediaTag(BaseModel):
    """Represents a media tag."""
    category: Optional[str]
    description: Optional[str]
    id: int
    isAdult: bool
    isGeneralSpoiler: bool
    isMediaSpoiler: bool
    name: str
    rank: Optional[int]


class MediaTitle(BaseModel):
    """Represents a media title. I think only romaji is guaranteed to exist, probably."""
    english: Optional[str]
    native: Optional[str]
    romaji: str
