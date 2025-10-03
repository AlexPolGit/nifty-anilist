from pathlib import Path
from unittest.mock import patch
import pytest

from nifty_anilist.settings import TokenSavingMethod
from nifty_anilist.auth import sign_in, get_auth_info, get_global_user, set_global_user, logout_global_user, remove_user


DOTENV_PATH = "test/integration/.env.test"
MOCK_USER_ID_1 = "1234"
MOCK_USER_ID_2 = "5678"
MOCK_AUTH_TOKEN_1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiIyMTI0MiIsInN1YiI6IjEyMzQiLCJleHAiOjQ4OTEzODEyMDB9.mb7CoDSN220-Pj5aEKfM_EH1h0gNBpq0y7rEgBEchHE"
MOCK_AUTH_TOKEN_2 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiIyMTI0MiIsInN1YiI6IjU2NzgiLCJleHAiOjQ4OTEzODEyMDB9.FQisbdGbVF8qM-RtTICeFaf4R-iXjDcNLC4Hlf5y40A"
MOCK_AUTH_TOKEN_CONTENTS_1 = {
    "header": {
        "alg": "HS256",
        "typ": "JWT"
    },
    "payload": {
        "aud": "21242",
        "sub": MOCK_USER_ID_1,
        "exp": 4891381200
    },
    "secret": "my-secret-string-for-encryption-123"
}
MOCK_AUTH_TOKEN_CONTENTS_2 = {
    "header": {
        "alg": "HS256",
        "typ": "JWT"
    },
    "payload": {
        "aud": "21242",
        "sub": MOCK_USER_ID_1,
        "exp": 4891381200
    },
    "secret": "my-secret-string-for-encryption-123"
}


class TestAuthenticationFunctions:

    @pytest.fixture(scope="session", autouse=True)
    def clear_env_file_after_tests(self):
        env_path = Path(DOTENV_PATH)
        yield

        # Empty the .env file.
        if env_path.exists():
            # Overwrite with empty content.
            env_path.write_text("")


    def test_multi_user_workflow(self):
        path_dotenv_path = patch("nifty_anilist.auth.DOTENV_PATH", DOTENV_PATH)
        patch_token_saving_method = patch("nifty_anilist.utils.auth_utils.anilist_settings.token_saving_method", TokenSavingMethod.IN_MEMORY)
        patch_generate_new_token = patch("nifty_anilist.auth.generate_new_token", side_effect=[MOCK_AUTH_TOKEN_1, MOCK_AUTH_TOKEN_2, MOCK_AUTH_TOKEN_2])
        
        with path_dotenv_path, patch_token_saving_method, patch_generate_new_token:
            # Test 1: Ensure you can get the auth info of a user either through the global user or directly.
            logout_global_user()
            assert get_global_user() == None

            user_1_auth_info = sign_in(set_global=True)
            global_user = get_global_user()
            assert global_user == user_1_auth_info.user_id

            user_1_auth_info = get_auth_info(user_1_auth_info.user_id)
            current_global_auth_info = get_auth_info()
            assert user_1_auth_info.token == current_global_auth_info.token

            # Test 2: Ensure logging out a user still keeps their token.
            logout_global_user()
            user_1_auth_info_after_logout = get_auth_info(user_1_auth_info.user_id)
            assert user_1_auth_info_after_logout.token == user_1_auth_info.token

            # Test 3: Log in a second user and swap users.
            user_2_auth_info = sign_in()
            assert user_1_auth_info.token != user_2_auth_info.token

            set_global_user(user_2_auth_info.user_id)
            assert get_global_user() != user_1_auth_info.user_id
            assert get_global_user() == user_2_auth_info.user_id
            
            set_global_user(user_1_auth_info.user_id)
            assert get_global_user() != user_2_auth_info.user_id
            assert get_global_user() == user_1_auth_info.user_id

            # Test 4: Try removing users.
            set_global_user(user_2_auth_info.user_id)
            remove_user()
            assert get_global_user() == None

            user_2_auth_info = sign_in()
            remove_user(user_2_auth_info.user_id)

