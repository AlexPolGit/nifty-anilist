from unittest.mock import patch

import pytest

from nifty_anilist.anilist_client import AnilistClient
from nifty_anilist.auth import AuthInfo
from nifty_anilist.client.custom_fields import (
    MediaListStatus,
    MediaType,
    MediaFormat,
    MediaSeason,
    MediaStatus
)
from nifty_anilist.settings import anilist_settings
from nifty_anilist.prebuilt import get_user_media_list, UserMediaListFilters, Timestamp, UserMediaEntry, MediaTag, MediaTitle


class TestMediaListFunctions:

    @pytest.fixture(autouse=True)
    def patch_user_info(self):
        if anilist_settings.test_user_id is None:
            raise ValueError("Test user ID not set in settings.")
        if anilist_settings.test_user_auth_token is None:
            raise ValueError("Test user auth token not set in settings.")

        with patch(
            "nifty_anilist.auth.get_auth_info",
            returns=AuthInfo(
                anilist_settings.test_user_id, anilist_settings.test_user_auth_token
            ),
        ) as user_info:
            self.user_info = user_info
            yield

    @pytest.mark.asyncio
    async def test_get_user_completed_anime_list(self):
        """Test to get all of a user's completed anime with a prebuilt function."""

        with self.user_info:
            async with AnilistClient() as client:
                filters = UserMediaListFilters(
                    type=MediaType.ANIME, status_in=[MediaListStatus.COMPLETED]
                )

                anime_list = await get_user_media_list(
                    client, user_name="AlexP", list_filters=filters
                )

                assert isinstance(anime_list, list)
                assert len(anime_list) > 500  # This Alex guy sure has a lot of anime.

                for anime in anime_list:
                    assert anime.advancedScores is None or isinstance(anime.advancedScores, dict)

                    assert isinstance(anime.completedAt, Timestamp)
                    assert anime.completedAt.year is None or isinstance(anime.completedAt.year, int)
                    assert anime.completedAt.month is None or isinstance(anime.completedAt.month, int)
                    assert anime.completedAt.day is None or isinstance(anime.completedAt.day, int)

                    assert isinstance(anime.createdAt, int)

                    assert anime.customLists is None or isinstance(anime.customLists, dict)

                    assert isinstance(anime.hiddenFromStatusLists, bool)

                    assert isinstance(anime.id, int)

                    assert isinstance(anime.media, UserMediaEntry)
                    validate_user_media_entry(anime.media)

                    assert isinstance(anime.mediaId, int)

                    assert anime.notes is None or isinstance(anime.notes, str)
                    
                    assert isinstance(anime.priority, int)

                    assert isinstance(anime.private, bool)

                    assert anime.progressVolumes is None or isinstance(anime.progressVolumes, int)

                    assert isinstance(anime.progress, int)

                    assert isinstance(anime.repeat, int)

                    assert isinstance(anime.score, float)

                    assert isinstance(anime.startedAt, Timestamp)
                    assert anime.startedAt.year is None or isinstance(anime.startedAt.year, int)
                    assert anime.startedAt.month is None or isinstance(anime.startedAt.month, int)
                    assert anime.startedAt.day is None or isinstance(anime.startedAt.day, int)

                    assert isinstance(anime.status, MediaListStatus)

                    assert anime.updatedAt is None or isinstance(anime.updatedAt, int)
                

def validate_user_media_entry(entry: UserMediaEntry):
    assert entry.averageScore is None or isinstance(entry.averageScore, int)

    assert entry.chapters is None or isinstance(entry.chapters, int)
    
    assert entry.countryOfOrigin is None or isinstance(entry.countryOfOrigin, str)

    assert entry.description is None or isinstance(entry.description, str)

    assert entry.duration is None or isinstance(entry.duration, int)

    assert isinstance(entry.endDate, Timestamp)
    assert entry.endDate.year is None or isinstance(entry.endDate.year, int)
    assert entry.endDate.month is None or isinstance(entry.endDate.month, int)
    assert entry.endDate.day is None or isinstance(entry.endDate.day, int)

    assert entry.episodes is None or isinstance(entry.episodes, int)

    assert entry.format is None or isinstance(entry.format, MediaFormat)

    assert isinstance(entry.genres, list)
    for genre in entry.genres:
        assert isinstance(genre, str)

    assert entry.hashtag is None or isinstance(entry.hashtag, str)

    assert isinstance(entry.id, int)

    assert entry.idMal is None or isinstance(entry.idMal, int)

    assert entry.isAdult is None or isinstance(entry.isAdult, bool)

    assert isinstance(entry.isFavourite, bool)

    assert entry.meanScore is None or isinstance(entry.meanScore, int)

    assert entry.season is None or isinstance(entry.season, MediaSeason)

    assert entry.seasonInt is None or isinstance(entry.seasonInt, int)

    assert entry.seasonYear is None or isinstance(entry.seasonYear, int)

    assert entry.source is None or isinstance(entry.source, str)

    assert isinstance(entry.startDate, Timestamp)
    assert entry.startDate.year is None or isinstance(entry.startDate.year, int)
    assert entry.startDate.month is None or isinstance(entry.startDate.month, int)
    assert entry.startDate.day is None or isinstance(entry.startDate.day, int)

    assert entry.status is None or isinstance(entry.status, MediaStatus)

    assert entry.synonyms is None or isinstance(entry.synonyms, list)
    if entry.synonyms:
        for synonym in entry.synonyms:
            isinstance(synonym, str)

    assert entry.tags is None or isinstance(entry.tags, list)
    for tag in entry.tags:
        isinstance(tag, MediaTag)

    assert isinstance(entry.title, MediaTitle)
    assert entry.title.english is None or isinstance(entry.title.english, str)
    assert entry.title.native is None or isinstance(entry.title.native, str)
    assert isinstance(entry.title.romaji, str)

    assert entry.volumes is None or isinstance(entry.volumes, int)
