from unittest.mock import MagicMock, patch

import pytest

from nifty_anilist.anilist_client import AnilistClient
from nifty_anilist.auth import AuthInfo
from nifty_anilist.client.custom_fields import (
    FuzzyDateFields,
    MediaFields,
    MediaListFields,
    MediaListSort,
    MediaListStatus,
    MediaTitleFields,
    MediaType,
    ScoreFormat,
    UserAvatarFields,
    UserFields,
)

from nifty_anilist.client.custom_queries import GraphQLField, Query
from nifty_anilist.settings import anilist_settings


class TestRequestFunctions:

    @pytest.fixture
    def mock_gql_request(self):
        return MagicMock(spec=GraphQLField)

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
    async def test_avatar_request(self):
        """Simple test to get a user's avatar."""

        with self.user_info:
            query = Query.user(name="robert").fields(  # Hi Robert!
                UserFields.avatar().fields(UserAvatarFields.large)
            )

            async with AnilistClient() as client:
                # Do query with global user.
                data = await client.anilist_request(query_request=query)

                # Access the avatar URL.
                avatar_url = data["User"]["avatar"]["large"]

                assert isinstance(avatar_url, str)
                assert avatar_url.startswith("https://s4.anilist.co/file/")

    @pytest.mark.asyncio
    async def test_manual_anime_list_request(self):
        """Test to get a user's completed anime list with a paginated request."""

        with self.user_info:
            async with AnilistClient() as client:
                query = Query.media_list(
                    user_name="AlexP",
                    type=MediaType.ANIME,
                    status_in=[MediaListStatus.COMPLETED],
                    sort=[MediaListSort.SCORE_DESC, MediaListSort.MEDIA_ID],
                ).fields(
                    MediaListFields.id,
                    MediaListFields.media_id,
                    MediaListFields.status,
                    MediaListFields.score(format=ScoreFormat.POINT_100),
                    MediaListFields.progress,
                    MediaListFields.started_at().fields(
                        FuzzyDateFields.year, FuzzyDateFields.month, FuzzyDateFields.day
                    ),
                    MediaListFields.completed_at().fields(
                        FuzzyDateFields.year, FuzzyDateFields.month, FuzzyDateFields.day
                    ),
                    MediaListFields.notes,
                    MediaListFields.hidden_from_status_lists,
                    MediaListFields.custom_lists(),
                    MediaListFields.media().fields(
                        MediaFields.title().fields(
                            MediaTitleFields.english(),
                            MediaTitleFields.native(),
                            MediaTitleFields.romaji(),
                        )
                    ),
                )

                response = await client.paginated_anilist_request(query)

                assert isinstance(response, list)
                assert len(response) > 500  # This Alex guy sure has a lot of anime.

                for anime in response:
                    assert isinstance(anime["id"], int)

                    assert isinstance(anime["mediaId"], int)

                    assert isinstance(anime["status"], str)

                    assert isinstance(anime["score"], int)

                    assert isinstance(anime["progress"], int)

                    assert isinstance(anime["startedAt"], dict)
                    assert "year" in anime["startedAt"]
                    assert anime["startedAt"]["year"] is None or isinstance(
                        anime["startedAt"]["year"], int
                    )
                    assert "month" in anime["startedAt"]
                    assert anime["startedAt"]["month"] is None or isinstance(
                        anime["startedAt"]["month"], int
                    )
                    assert "day" in anime["startedAt"]
                    assert anime["startedAt"]["day"] is None or isinstance(
                        anime["startedAt"]["day"], int
                    )

                    assert isinstance(anime["completedAt"], dict)
                    assert "year" in anime["completedAt"]
                    assert anime["completedAt"]["year"] is None or isinstance(
                        anime["completedAt"]["year"], int
                    )
                    assert "month" in anime["completedAt"]
                    assert anime["completedAt"]["month"] is None or isinstance(
                        anime["completedAt"]["month"], int
                    )
                    assert "day" in anime["completedAt"]
                    assert anime["completedAt"]["day"] is None or isinstance(
                        anime["completedAt"]["day"], int
                    )

                    assert anime["notes"] is None or isinstance(anime["notes"], str)

                    assert isinstance(anime["hiddenFromStatusLists"], bool)

                    assert isinstance(anime["media"], dict)

                    assert "title" in anime["media"]
                    assert isinstance(anime["media"]["title"], dict)
                    assert "english" in anime["media"]["title"]
                    assert "native" in anime["media"]["title"]
                    assert "romaji" in anime["media"]["title"]
                    assert anime["media"]["title"]["english"] is None or isinstance(
                        anime["media"]["title"]["english"], str
                    )
                    assert anime["media"]["title"]["native"] is None or isinstance(
                        anime["media"]["title"]["native"], str
                    )
                    assert isinstance(anime["media"]["title"]["romaji"], str)
