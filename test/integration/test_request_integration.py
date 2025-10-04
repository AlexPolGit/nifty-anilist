from pathlib import Path
from unittest.mock import patch
import pytest
from gql import gql

from nifty_anilist.auth import AuthInfo
from nifty_anilist.request import anilist_request
from nifty_anilist.settings import anilist_settings


DOTENV_PATH = "test/integration/.env.test"


class TestRequestFunctions():
    
    @pytest.fixture(scope="session", autouse=True)
    def clear_env_file_after_tests(self):
        env_path = Path(DOTENV_PATH)
        yield

        # Empty the .env file.
        if env_path.exists():
            # Overwrite with empty content.
            env_path.write_text("")

    @pytest.mark.asyncio
    async def test_simple_anilist_request(self):
        """Simple test to get a user's avatar."""

        if anilist_settings.test_user_id is None:
            raise ValueError("Test user ID not set in settings.")
        if anilist_settings.test_user_auth_token is None:
            raise ValueError("Test user ID not set in settings.")

        patch_user_info = patch("nifty_anilist.auth.get_auth_info", returns=AuthInfo(anilist_settings.test_user_id, anilist_settings.test_user_auth_token))

        with patch_user_info:
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
