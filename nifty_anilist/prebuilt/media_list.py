from typing import List, Optional, Any
from pydantic import BaseModel, model_validator

from nifty_anilist.client import MediaType, MediaListStatus, MediaListSort, ScoreFormat, MediaFormat, MediaSeason, MediaStatus
from nifty_anilist.client.custom_fields import MediaListFields, MediaFields, MediaTitleFields, FuzzyDateFields, MediaTagFields
from nifty_anilist.client.custom_queries import Query

from nifty_anilist import AnilistClient, Timestamp, MediaTag, MediaTitle


class UserMediaListFilters(BaseModel):
    user_id: Optional[int] = None
    """Anilist ID of the user. Must be provided if user_name is not."""

    user_name: Optional[str] = None
    """Anilist user name of the user. Must be provided if user_id is not."""

    @model_validator(mode='after')
    def ensure_id_or_name(self):
        """Ensure that either a user ID or user name are provided, but not both."""
        if (self.user_id is None and self.user_name is None) or (self.user_id and self.user_name):
            raise ValueError("Please provide one of either \"user_id\" or \"user_name\" in the media list filters (not both).")
        return self

    type: Optional[MediaType] = None
    """Type of media to return (anime or manga). Leave as `None` for both."""

    status_in: Optional[List[MediaListStatus]] = None
    """Allowed statuses of the media. Leave as `None` for any."""

    started_at_greater: Optional[int] = None
    """Minimum datetime for when this media was started. Use an integer in the `YYYYMMDD` format. Leave as `None` for no minimum."""

    started_at_lesser: Optional[int] = None
    """Maximum datetime for when this media was started. Use an integer in the `YYYYMMDD` format. Leave as `None` for no maximum."""

    completed_at_greater: Optional[int] = None
    """Minimum datetime for when this media was completed. Use an integer in the `YYYYMMDD` format. Leave as `None` for no minimum."""

    completed_at_lesser: Optional[int] = None
    """Maximum datetime for when this media was completed. Use an integer in the `YYYYMMDD` format. Leave as `None` for no maximum."""

    sort: Optional[List[MediaListSort]] = [MediaListSort.SCORE_DESC, MediaListSort.MEDIA_ID]
    """Defines how to sort the list of media. Default is sort by score (descending) and then media ID for things with the same score."""

    score_format: ScoreFormat = ScoreFormat.POINT_100
    """What format to display scored in. Default is score out of 100."""


class UserMediaEntry(BaseModel):
    """Represents the media details for a media entry in a user's list."""
    averageScore: Optional[int]
    chapters: Optional[int]
    countryOfOrigin: str
    description: Optional[str]
    duration: Optional[int]
    endDate: Timestamp
    episodes: Optional[int]
    format: Optional[MediaFormat]
    genres: List[str]
    hashtag: Optional[str]
    id: int
    idMal: Optional[int]
    isAdult: bool
    isFavourite: bool
    meanScore: Optional[int]
    season: Optional[MediaSeason]
    seasonInt: Optional[int]
    seasonYear: Optional[int]
    source: Optional[str]
    startDate: Timestamp
    status: MediaStatus
    synonyms: List[str]
    tags: List[MediaTag]
    title: MediaTitle
    volumes: Optional[int]


class UserMediaListEntry(BaseModel):
    """Represents one media entry for a user's list."""
    advancedScores: Any
    completedAt: Timestamp
    createdAt: int
    customLists: Any
    hiddenFromStatusLists: bool
    id: int
    media: UserMediaEntry
    mediaId: int
    notes: Optional[str]
    priority: int
    private: bool
    progressVolumes: Optional[int]
    progress: int
    repeat: int
    score: float
    startedAt: Timestamp
    status: MediaListStatus
    updatedAt: Optional[int]


async def get_user_media_list(
        client: AnilistClient,
        list_filters: UserMediaListFilters
    ) -> List[UserMediaListEntry]:
    """Get an Anilist user's media list.
    
    Args:
        client: Anilist client to use when making the request.
        list_filters: List of filters to use. Make sure provide either a user ID or user name.

    Returns:
        media_list: List of media from a user's list.
    """

    query = Query.media_list(
        user_id=list_filters.user_id,
        user_name=list_filters.user_name,
        type=list_filters.type,
        status_in=list_filters.status_in,
        started_at_greater=list_filters.started_at_greater,
        started_at_lesser=list_filters.started_at_lesser,
        completed_at_greater=list_filters.completed_at_greater,
        completed_at_lesser=list_filters.completed_at_lesser,
        sort=list_filters.sort
    ).fields(
        MediaListFields.advanced_scores,
        MediaListFields.completed_at().fields(
            FuzzyDateFields.year, FuzzyDateFields.month, FuzzyDateFields.day
        ),
        MediaListFields.created_at,
        MediaListFields.custom_lists(as_array=True),
        MediaListFields.hidden_from_status_lists,
        MediaListFields.id,
        MediaListFields.media().fields(
            MediaFields.average_score,
            MediaFields.chapters,
            MediaFields.country_of_origin,
            MediaFields.description(),
            MediaFields.duration,
            MediaFields.end_date().fields(
                FuzzyDateFields.year, FuzzyDateFields.month, FuzzyDateFields.day
            ),
            MediaFields.episodes,
            MediaFields.format,
            MediaFields.genres,
            MediaFields.hashtag,
            MediaFields.id,
            MediaFields.id_mal,
            MediaFields.is_adult,
            MediaFields.is_favourite,
            MediaFields.mean_score,
            MediaFields.season,
            MediaFields.season_int,
            MediaFields.season_year,
            MediaFields.source(),
            MediaFields.start_date().fields(
                FuzzyDateFields.year, FuzzyDateFields.month, FuzzyDateFields.day
            ),
            MediaFields.status(),
            MediaFields.synonyms,
            MediaFields.tags().fields(
                MediaTagFields.category,
                MediaTagFields.description,
                MediaTagFields.id,
                MediaTagFields.is_adult,
                MediaTagFields.is_general_spoiler,
                MediaTagFields.is_media_spoiler,
                MediaTagFields.name,
                MediaTagFields.rank
            ),
            MediaFields.title().fields(
                MediaTitleFields.english(),
                MediaTitleFields.native(),
                MediaTitleFields.romaji(),
            ),
            MediaFields.volumes
        ),
        MediaListFields.media_id,
        MediaListFields.notes,
        MediaListFields.priority,
        MediaListFields.private,
        MediaListFields.progress,
        MediaListFields.progress_volumes,
        MediaListFields.repeat,
        MediaListFields.score(format=list_filters.score_format),
        MediaListFields.started_at().fields(
            FuzzyDateFields.year, FuzzyDateFields.month, FuzzyDateFields.day
        ),
        MediaListFields.status,
        MediaListFields.updated_at,
    )

    response = await client.paginated_anilist_request(query)
    media_list: List[UserMediaListEntry] = []

    for item in response:
        media_list.append(UserMediaListEntry(**item))

    return media_list
