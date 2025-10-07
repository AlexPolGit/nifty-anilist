from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from nifty_anilist.anilist_client import AnilistClient
from nifty_anilist.auth import AuthInfo
from nifty_anilist.client.custom_fields import (
    MediaListStatus,
    MediaType,
    MediaFormat,
    MediaSeason,
    MediaStatus,
    MediaSource,
    MediaSort
)
from nifty_anilist.settings import anilist_settings
from nifty_anilist.prebuilt import get_media_list, MediaListFilters, MediaListEntry, MediaStats, MediaScoreDistribution, MediaStatusDistribution, MediaCoverImage, Timestamp, MediaTag, MediaTitle


class TestMediaFunctions:

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
    async def test_get_recent_anime(self):
        """Test to get some recently aired (completed) anime with a prebuilt function."""

        with self.user_info:
            async with AnilistClient() as client:
                one_year_ago = datetime.today() - timedelta(days=365)
                fuzz_date = int(one_year_ago.strftime("%Y%m%d"))

                filters = MediaListFilters(
                    type=MediaType.ANIME,
                    status_in=[MediaStatus.FINISHED],
                    start_date_greater=fuzz_date,
                )
                anime_list = await get_media_list(client, list_filters=filters)

                assert isinstance(anime_list, list)
                assert len(anime_list) > 0  # Can you imagine if this failed?

                for anime in anime_list:
                    validate_media_entry(anime)

    @pytest.mark.asyncio
    async def test_get_popular_manga(self):
        """Test to get the most popular completed manga with a prebuilt function."""

        with self.user_info:
            async with AnilistClient() as client:
                filters = MediaListFilters(
                    type=MediaType.MANGA, sort=[MediaSort.SCORE_DESC], max_media_count=100
                )
                manga_list = await get_media_list(client, list_filters=filters)

                assert isinstance(manga_list, list)
                assert len(manga_list) > 0

                for manga in manga_list:
                    validate_media_entry(manga)


def validate_media_entry(entry: MediaListEntry):
    assert entry.averageScore is None or isinstance(entry.averageScore, int)

    assert entry.bannerImage is None or isinstance(entry.bannerImage, str)

    assert entry.chapters is None or isinstance(entry.chapters, int)

    assert entry.countryOfOrigin is None or isinstance(entry.countryOfOrigin, str)

    assert isinstance(entry.coverImage, MediaCoverImage)
    assert entry.coverImage.extraLarge is None or isinstance(entry.coverImage.extraLarge, str)

    assert entry.description is None or isinstance(entry.description, str)

    assert entry.duration is None or isinstance(entry.duration, int)

    assert isinstance(entry.endDate, Timestamp)
    assert entry.endDate.year is None or isinstance(entry.endDate.year, int)
    assert entry.endDate.month is None or isinstance(entry.endDate.month, int)
    assert entry.endDate.day is None or isinstance(entry.endDate.day, int)

    assert entry.episodes is None or isinstance(entry.episodes, int)

    assert entry.favourites is None or isinstance(entry.favourites, int)

    assert entry.format is None or isinstance(entry.format, MediaFormat)

    assert entry.genres is None or isinstance(entry.genres, list)
    if entry.genres:
        for genre in entry.genres:
            assert isinstance(genre, str)

    assert entry.hashtag is None or isinstance(entry.hashtag, str)

    assert isinstance(entry.id, int)

    assert entry.idMal is None or isinstance(entry.idMal, int)

    assert entry.isAdult is None or isinstance(entry.isAdult, bool)

    assert entry.isFavourite is None or isinstance(entry.isFavourite, bool)

    assert entry.isLicensed is None or isinstance(entry.isLicensed, bool)

    assert entry.meanScore is None or isinstance(entry.meanScore, int)

    assert entry.modNotes is None or isinstance(entry.modNotes, str)

    assert entry.popularity is None or isinstance(entry.popularity, int)

    assert entry.season is None or isinstance(entry.season, MediaSeason)

    assert entry.seasonInt is None or isinstance(entry.seasonInt, int)

    assert entry.seasonYear is None or isinstance(entry.seasonYear, int)

    assert entry.siteUrl is None or isinstance(entry.siteUrl, str)

    assert entry.source is None or isinstance(entry.source, MediaSource)

    assert isinstance(entry.startDate, Timestamp)
    assert entry.startDate.year is None or isinstance(entry.startDate.year, int)
    assert entry.startDate.month is None or isinstance(entry.startDate.month, int)
    assert entry.startDate.day is None or isinstance(entry.startDate.day, int)

    assert isinstance(entry.stats, MediaStats)
    assert entry.stats.scoreDistribution is None or isinstance(entry.stats.scoreDistribution, list)
    if entry.stats.scoreDistribution:
        for score in entry.stats.scoreDistribution:
            assert isinstance(score, MediaScoreDistribution)
            assert score.score is None or isinstance(score.score, int)
            assert score.amount is None or isinstance(score.amount, int)
    assert entry.stats.statusDistribution is None or isinstance(entry.stats.statusDistribution, list)
    if entry.stats.statusDistribution:
        for status in entry.stats.statusDistribution:
            assert isinstance(status, MediaStatusDistribution)
            assert status.status is None or isinstance(status.status, MediaListStatus)
            assert status.amount is None or isinstance(status.amount, int)

    assert entry.status is None or isinstance(entry.status, MediaStatus)

    assert entry.synonyms is None or isinstance(entry.synonyms, list)
    if entry.synonyms:
        for synonym in entry.synonyms:
            assert isinstance(synonym, str)

    assert entry.tags is None or isinstance(entry.tags, list)
    if entry.tags:
        for tag in entry.tags:
            assert isinstance(tag, MediaTag)
    
    assert isinstance(entry.title, MediaTitle)
    assert entry.title.english is None or isinstance(entry.title.english, str)
    assert entry.title.native is None or isinstance(entry.title.native, str)
    assert isinstance(entry.title.romaji, str)

    assert entry.trending is None or isinstance(entry.trending, int)

    assert entry.type is None or isinstance(entry.type, MediaType)

    assert entry.updatedAt is None or isinstance(entry.updatedAt, int)

    assert entry.volumes is None or isinstance(entry.volumes, int)
