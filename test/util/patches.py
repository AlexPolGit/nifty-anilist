from unittest.mock import patch

import pytest

from test.conftest import DOTENV_PATH


@pytest.fixture
def patch_auth_dotenv_path():
    with patch("nifty_anilist.auth.DOTENV_PATH", DOTENV_PATH) as patch_dotenv_path:
        yield patch_dotenv_path
