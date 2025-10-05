from unittest.mock import patch, MagicMock
import pytest
from gql import gql, GraphQLRequest

from nifty_anilist.auth import AuthInfo
from nifty_anilist.request import anilist_request
from nifty_anilist.settings import anilist_settings


class TestRequestFunctions():

    @pytest.fixture
    def mock_gql_request(self):
        return MagicMock(spec=GraphQLRequest)

    @pytest.fixture(autouse=True)
    def patch_user_info(self):
        if anilist_settings.test_user_id is None:
            raise ValueError("Test user ID not set in settings.")
        if anilist_settings.test_user_auth_token is None:
            raise ValueError("Test user auth token not set in settings.")
        
        with patch("nifty_anilist.auth.get_auth_info", returns=AuthInfo(anilist_settings.test_user_id, anilist_settings.test_user_auth_token)) as user_info:
            self.user_info = user_info
            yield


    @pytest.mark.asyncio
    async def test_simple_anilist_request(self):
        """Simple test to get a user's avatar."""

        with self.user_info:
            query = gql("""
                query GetUserAvatar($name: String) {
                    User(name: $name) {
                        avatar {
                            large
                        }
                    }
                }
            """)

            query.variable_values = {
                "name": "robert" # Hi Robert!
            }

            # Do query with global user.
            data = await anilist_request(query_request=query)

            # Access the avatar URL.
            avatar_url = data["User"]["avatar"]["large"]
            
            assert isinstance(avatar_url, str)
            assert avatar_url.startswith("https://s4.anilist.co/file/")
