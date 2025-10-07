from typing import Annotated, Any, Dict, List, Optional

from pydantic import AfterValidator, BaseModel

from nifty_anilist import AnilistClient, get_global_user
from nifty_anilist.client import (
    MediaFormat,
    MediaListSort,
    MediaListStatus,
    MediaSeason,
    MediaStatus,
    MediaType,
    ScoreFormat,
)
from nifty_anilist.client.custom_fields import (
    FuzzyDateFields,
    MediaFields,
    MediaListFields,
    MediaTagFields,
    MediaTitleFields,
)
from nifty_anilist.client.custom_queries import Query
from nifty_anilist.prebuilt import MediaTag, MediaTitle, Timestamp
from nifty_anilist.utils.auth_utils import UserId
from nifty_anilist.utils.model_utils import validate_fuzzy_date_int


class UserMediaListFilters(BaseModel):
    completed_at_greater: Annotated[
        Optional[int], AfterValidator(validate_fuzzy_date_int)
    ] = None
    """Minimum datetime for when this media was completed. Use an integer in the `YYYYMMDD` format. Leave as `None` for no minimum."""

    completed_at_lesser: Annotated[
        Optional[int], AfterValidator(validate_fuzzy_date_int)
    ] = None
    """Maximum datetime for when this media was completed. Use an integer in the `YYYYMMDD` format. Leave as `None` for no maximum."""

    started_at_greater: Annotated[
        Optional[int], AfterValidator(validate_fuzzy_date_int)
    ] = None
    """Minimum datetime for when this media was started. Use an integer in the `YYYYMMDD` format. Leave as `None` for no minimum."""

    started_at_lesser: Annotated[
        Optional[int], AfterValidator(validate_fuzzy_date_int)
    ] = None
    """Maximum datetime for when this media was started. Use an integer in the `YYYYMMDD` format. Leave as `None` for no maximum."""

    status_in: Optional[List[MediaListStatus]] = None
    """Allowed statuses for the media. Leave as `None` for any."""

    score_format: ScoreFormat = ScoreFormat.POINT_100
    """What format to display scored in. Default is score out of 100."""

    sort: Optional[List[MediaListSort]] = [
        MediaListSort.SCORE_DESC,
        MediaListSort.MEDIA_ID,
    ]
    """Defines how to sort the list of media. Default is sort by score (descending) and then media ID for things with the same score."""

    type: Optional[MediaType] = None
    """Type of media to return (anime or manga). Leave as `None` for both."""


class UserMediaEntry(BaseModel):
    """Represents the details for a media entry in a user's list.
    **Note:** This is not all of the possible ones, just the ones for this helper class.
    """

    averageScore: Optional[int]
    chapters: Optional[int]
    countryOfOrigin: Optional[str]
    description: Optional[str]
    duration: Optional[int]
    endDate: Timestamp
    episodes: Optional[int]
    format: Optional[MediaFormat]
    genres: List[str]
    hashtag: Optional[str]
    id: int
    idMal: Optional[int]
    isAdult: Optional[bool]
    isFavourite: bool
    meanScore: Optional[int]
    season: Optional[MediaSeason]
    seasonInt: Optional[int]
    seasonYear: Optional[int]
    source: Optional[str]
    startDate: Timestamp
    status: MediaStatus
    synonyms: Optional[List[str]]
    tags: List[MediaTag]
    title: MediaTitle
    volumes: Optional[int]


class UserMediaListEntry(BaseModel):
    """Represents one media entry for a user's list."""

    advancedScores: Optional[Dict[str, Any]]
    completedAt: Timestamp
    createdAt: int
    customLists: Optional[Dict[str, Any]]
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
    user_id: Optional[UserId] = None,
    user_name: Optional[str] = None,
    list_filters: UserMediaListFilters = UserMediaListFilters(),
) -> List[UserMediaListEntry]:
    """Get an Anilist user's media list.

    Args:
        client: Anilist client to use when making the request.
        user_id: Anilist ID of the user. Must be provided if user_name is not.
        user_name: Anilist user name of the user. Must be provided if user_id is not.
        list_filters: List of filters to use.

    Returns:
        media_list: List of media from a user's list.
    """

    if (user_id is None and user_name is None) or (user_id and user_name):
        raise ValueError(
            'Please provide one of either "user_id" or "user_name" (not both).'
        )

    query = Query.media_list(
        completed_at_greater=list_filters.completed_at_greater,
        completed_at_lesser=list_filters.completed_at_lesser,
        sort=list_filters.sort,
        started_at_greater=list_filters.started_at_greater,
        started_at_lesser=list_filters.started_at_lesser,
        status_in=list_filters.status_in,
        type=list_filters.type,
        user_id=int(user_id) if user_id else None,
        user_name=user_name,
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
                MediaTagFields.rank,
            ),
            MediaFields.title().fields(
                MediaTitleFields.english(),
                MediaTitleFields.native(),
                MediaTitleFields.romaji(),
            ),
            MediaFields.volumes,
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


async def get_my_media_list(
    client: AnilistClient,
    list_filters: UserMediaListFilters = UserMediaListFilters(),
) -> List[UserMediaListEntry]:
    """Get media list of the current global user.

    Args:
        client: Anilist client to use when making the request.
        list_filters: List of filters to use.

    Returns:
        media_list: Media list of the current global user.
    """

    return await get_user_media_list(
        client,
        user_id=get_global_user(raise_if_missing=True),
        list_filters=list_filters,
    )
