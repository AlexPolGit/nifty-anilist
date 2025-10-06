from unittest.mock import MagicMock, patch

import pytest
from nifty_anilist.anilist_client import AnilistClient

from nifty_anilist.auth import AuthInfo
from nifty_anilist.client.custom_fields import UserAvatarFields, UserFields

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
    async def test_simple_anilist_request(self):
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
