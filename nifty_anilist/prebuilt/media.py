from typing import Annotated, List, Optional

from pydantic import AfterValidator, BaseModel

from nifty_anilist import AnilistClient

from nifty_anilist.client import (
    MediaFormat,
    MediaSeason,
    MediaSort,
    MediaSort,
    MediaSource,
    MediaStatus,
    MediaType,
)
from nifty_anilist.client.custom_fields import (
    FuzzyDateFields,
    MediaCoverImageFields,
    MediaListStatus,
    MediaStatsFields,
    MediaTagFields,
    MediaTitleFields,
    ScoreDistributionFields,
    StatusDistributionFields,
)
from nifty_anilist.client.custom_queries import MediaFields, Query
from nifty_anilist.prebuilt import Timestamp
from nifty_anilist.utils.model_utils import validate_fuzzy_date_int


class MediaListFilters(BaseModel):
    average_score_greater: Optional[int] = None
    """Minimum average score for the media. Leave as `None` for no minimum."""

    average_score_lesser: Optional[int] = None
    """Maximum average score for the media. Leave as `None` for no maximum."""

    chapters_greater: Optional[int] = None
    """Minimum chapter count for the media. Leave as `None` for no minimum."""

    chapters_lesser: Optional[int] = None
    """Maximum chapter count for the media. Leave as `None` for no maximum."""

    country_of_origin: Optional[str] = None
    """Country of origin for the media. Leave as `None` for any. Ex: \"JP\", \"CN\", \"KR\", etc."""

    duration_greater: Optional[int] = None
    """Minimum episode duration for the media. Leave as `None` for no minimum."""

    duration_lesser: Optional[int] = None
    """Maximum episode duration for the media. Leave as `None` for no maximum."""

    end_date_greater: Annotated[
        Optional[int], AfterValidator(validate_fuzzy_date_int)
    ] = None
    """Minimum datetime for when this media ended. Use an integer in the `YYYYMMDD` format. Leave as `None` for no minimum."""

    end_date_lesser: Annotated[
        Optional[int], AfterValidator(validate_fuzzy_date_int)
    ] = None
    """Maximum datetime for when this media ended. Use an integer in the `YYYYMMDD` format. Leave as `None` for no maximum."""

    episodes_greater: Optional[int] = None
    """Minimum episode count for the media. Leave as `None` for no minimum."""

    episodes_lesser: Optional[int] = None
    """Maximum episode count for the media. Leave as `None` for no maximum."""

    format_in: Optional[List[MediaFormat]] = None
    """Allowed formats for the media. Leave as `None` for any."""

    genre_in: Optional[List[str]] = None
    """Allowed genres for the media. Leave as `None` for any."""

    id_in: Optional[List[int]] = None
    """Allowed Anilist media IDs for the media. Leave as `None` for any."""

    id_mal_in: Optional[List[int]] = None
    """Allowed MAL media IDs for the media. Leave as `None` for any."""

    is_adult: Optional[bool] = None
    """Set to `True` for media marked as 18+. Set to `False` for media *not* marked as 18+. Leave as `None` for any."""

    is_licensed: Optional[bool] = None
    """Is the media licensed? Leave as `None` for any."""

    licensed_by_in: Optional[List[str]] = None
    """Allowed licensees for the media. Leave as `None` for any."""

    max_media_count: int = 100
    """Max number of media to return from the query. Default is 100."""

    minimum_tag_rank: Optional[int] = None
    """Only apply the tags filter argument to tags above this rank. Leave as `None` for no minimum, though Anilist has a built-in default of 18."""

    on_list: Optional[bool] = None
    """If `True`, only get media that are on the logged-in user's list. Useful for when you need a user list with filters that are not available in the `mediaList` query."""

    popularity_greater: Optional[int] = None
    """Minimum popularity for the media. Leave as `None` for no minimum."""

    popularity_lesser: Optional[int] = None
    """Maximum popularity for the media. Leave as `None` for no maximum."""

    search: Optional[str] = None
    """Search string to use for the media. This is similar to Anilist's search bar."""

    season: Optional[MediaSeason] = None
    """Season when the media aired. Leave as `None` for any."""

    season_year: Optional[int] = None
    """Year of the season when the media aired. Leave as `None` for any."""

    sort: Optional[List[MediaSort]] = [MediaSort.ID]
    """Defines how to sort the list of media. Default is sort by media ID."""

    source_in: Optional[List[MediaSource]] = None
    """Allowed sources for the media. Leave as `None` for any."""

    start_date_greater: Annotated[
        Optional[int], AfterValidator(validate_fuzzy_date_int)
    ] = None
    """Minimum datetime for when this media started. Use an integer in the `YYYYMMDD` format. Leave as `None` for no minimum."""

    start_date_lesser: Annotated[
        Optional[int], AfterValidator(validate_fuzzy_date_int)
    ] = None
    """Maximum datetime for when this media started. Use an integer in the `YYYYMMDD` format. Leave as `None` for no maximum."""

    status_in: Optional[List[MediaStatus]] = None
    """Allowed statuses for the media. Leave as `None` for any."""

    tag_in: Optional[List[str]] = None
    """Allowed tags for the media. Leave as `None` for any."""

    tag_category_in: Optional[List[str]] = None
    """Allowed tag categories for the media. Leave as `None` for any."""

    type: Optional[MediaType] = None
    """Type of media to return (anime or manga). Leave as `None` for both."""

    volumes_greater: Optional[int] = None
    """Minimum volume count for the media. Leave as `None` for no minimum."""

    volumes_lesser: Optional[int] = None
    """Maximum volume count for the media. Leave as `None` for no maximum."""


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


class MediaCoverImage(BaseModel):
    """Represents a media cover image. We only care about the extra large one."""

    extraLarge: Optional[str]


class MediaScoreDistribution(BaseModel):
    """Represents a single score for a media and how many users have that score."""

    score: Optional[int]
    amount: Optional[int]


class MediaStatusDistribution(BaseModel):
    """Represents a single watching/reading status for a media and how many users have that status."""

    status: Optional[MediaListStatus]
    amount: Optional[int]


class MediaStats(BaseModel):
    """Represents the user score distributions and watching/reading status distributions for a media."""

    scoreDistribution: Optional[List[MediaScoreDistribution]]
    statusDistribution: Optional[List[MediaStatusDistribution]]


class MediaListEntry(BaseModel):
    """Represents the all the details that we query for a media entry.
    **Note:** This is not all of the possible ones, just the ones for this helper class.
    """

    averageScore: Optional[int]
    bannerImage: Optional[str]
    chapters: Optional[int]
    countryOfOrigin: Optional[str]
    coverImage: MediaCoverImage
    description: Optional[str]
    duration: Optional[int]
    endDate: Timestamp
    episodes: Optional[int]
    favourites: Optional[int]
    format: MediaFormat
    genres: Optional[List[str]]
    hashtag: Optional[str]
    id: int
    idMal: Optional[int]
    isAdult: Optional[bool]
    isFavourite: bool
    isLicensed: Optional[bool]
    meanScore: Optional[int]
    modNotes: Optional[str]
    popularity: Optional[int]
    season: Optional[MediaSeason]
    seasonInt: Optional[int]
    seasonYear: Optional[int]
    siteUrl: Optional[str]
    source: Optional[MediaSource]
    startDate: Timestamp
    stats: MediaStats
    status: MediaStatus
    synonyms: Optional[List[str]]
    tags: Optional[List[MediaTag]]
    title: MediaTitle
    trending: Optional[int]
    type: MediaType
    updatedAt: Optional[int]
    volumes: Optional[int]


async def get_media_list(
    client: AnilistClient,
    list_filters: MediaListFilters = MediaListFilters(),
) -> List[MediaListEntry]:
    """Get a list of media with high-level details.
    This function will not return more granular results for each media like character/staff lists, airing schedules, etc.

    Args:
        client: Anilist client to use when making the request.
        user_id: Anilist ID of the user. Must be provided if user_name is not.
        user_name: Anilist user name of the user. Must be provided if user_id is not.
        list_filters: List of filters to use.

    Returns:
        media_list: List of media from a user's list.
    """

    query = Query.media(
        average_score_greater=list_filters.average_score_greater,
        average_score_lesser=list_filters.average_score_lesser,
        chapters_greater=list_filters.chapters_greater,
        chapters_lesser=list_filters.chapters_lesser,
        country_of_origin=list_filters.country_of_origin,
        duration_greater=list_filters.duration_greater,
        duration_lesser=list_filters.duration_lesser,
        end_date_greater=list_filters.end_date_greater,
        end_date_lesser=list_filters.end_date_lesser,
        episodes_greater=list_filters.episodes_greater,
        episodes_lesser=list_filters.episodes_lesser,
        format_in=list_filters.format_in,
        genre_in=list_filters.genre_in,
        id_in=list_filters.id_in,
        id_mal_in=list_filters.id_mal_in,
        is_adult=list_filters.is_adult,
        is_licensed=list_filters.is_licensed,
        licensed_by_in=list_filters.licensed_by_in,
        minimum_tag_rank=list_filters.minimum_tag_rank,
        on_list=list_filters.on_list,
        popularity_greater=list_filters.popularity_greater,
        popularity_lesser=list_filters.popularity_lesser,
        search=list_filters.search,
        season=list_filters.season,
        season_year=list_filters.season_year,
        sort=list_filters.sort,
        source_in=list_filters.source_in,
        start_date_greater=list_filters.start_date_greater,
        start_date_lesser=list_filters.start_date_lesser,
        status_in=list_filters.status_in,
        tag_in=list_filters.tag_in,
        tag_category_in=list_filters.tag_category_in,
        type=list_filters.type,
        volumes_greater=list_filters.volumes_greater,
        volumes_lesser=list_filters.volumes_lesser,
    ).fields(
        MediaFields.average_score,
        MediaFields.banner_image,
        MediaFields.chapters,
        MediaFields.country_of_origin,
        MediaFields.cover_image().fields(MediaCoverImageFields.extra_large),
        MediaFields.description(),
        MediaFields.duration,
        MediaFields.end_date().fields(
            FuzzyDateFields.year, FuzzyDateFields.month, FuzzyDateFields.day
        ),
        MediaFields.episodes,
        MediaFields.favourites,
        MediaFields.format,
        MediaFields.genres,
        MediaFields.hashtag,
        MediaFields.id,
        MediaFields.id_mal,
        MediaFields.is_adult,
        MediaFields.is_favourite,
        MediaFields.is_licensed,
        MediaFields.mean_score,
        MediaFields.mod_notes,
        MediaFields.popularity,
        MediaFields.season,
        MediaFields.season_int,
        MediaFields.season_year,
        MediaFields.site_url,
        MediaFields.source(),
        MediaFields.start_date().fields(
            FuzzyDateFields.year, FuzzyDateFields.month, FuzzyDateFields.day
        ),
        MediaFields.stats().fields(
            MediaStatsFields.score_distribution().fields(
                ScoreDistributionFields.score, ScoreDistributionFields.amount
            ),
            MediaStatsFields.status_distribution().fields(
                StatusDistributionFields.status, StatusDistributionFields.amount
            ),
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
        MediaFields.trending,
        MediaFields.type,
        MediaFields.updated_at,
        MediaFields.volumes,
    )

    response = await client.paginated_anilist_request(
        query, max_items=list_filters.max_media_count
    )
    media_list: List[MediaListEntry] = []

    for item in response:
        media_list.append(MediaListEntry(**item))

    return media_list
