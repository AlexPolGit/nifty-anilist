from typing import Optional
from enum import StrEnum
from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenSavingMethod(StrEnum):
    """Enum for types of token-saving methods."""

    KEYRING = "KEYRING"
    IN_MEMORY = "IN_MEMORY"


class WebBrowser(StrEnum):
    """Enum for supported browsers."""

    CHROME = "CHROME"
    FIREFOX = "FIREFOX"
    EDGE = "EDGE"
    IE = "IE"
    SAFARI = "SAFARI"


class AnilistSettings(BaseSettings):
    """Settings for Anilist-related things.
    Will be populated from environment variables or the local `.env` file.
    """

    # Configuration for the settings object.
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_prefix="ANILIST_"
    )

    # --- General ---
    api_url: str = "https://graphql.anilist.co"
    auth_url: str = "https://anilist.co/api/v2/oauth/authorize"
    token_url: str = "https://anilist.co/api/v2/oauth/token"

    # --- Requests ---
    request_timeout_seconds: int = 10
    """Number of seconds to wait for a single API request to Anilist to complete."""

    rate_limit_max_retries: Optional[int] = None
    """Number of times to retry failed requests to the Anilist API after a rate limit error. Set to `None` for infinite retries."""

    rate_limit_retry_initial_delay: Optional[int] = None
    """Amount to wait before retrying a request after a rate limit error. Set to `None` to use the value from headers instead."""

    max_requests_per_minute: Optional[int] = None
    """Max number of requests to make per minute. This can help avoid rate limiting before it happens.
    Set to `None` to not have an explicit limit and instead rely on the headers from Anilist."""

    # --- Auth ---
    client_id: str
    """Client ID from Anilist client.
    Reference: https://docs.anilist.co/guide/auth/#creating-an-application and https://anilist.co/settings/developer"""

    client_secret: str
    """Client secret from Anilist client.
    Reference: https://docs.anilist.co/guide/auth/#creating-an-application and https://anilist.co/settings/developer"""

    client_redirect_url: str
    """Client redirect URL from Anilist client.
    Reference: https://docs.anilist.co/guide/auth/#creating-an-application and https://anilist.co/settings/developer"""

    auth_code_browser: WebBrowser = WebBrowser.CHROME
    """Browser to use when getting auth code from browser. Possbile values: \"CHROME\", \"FIREFOX\", \"EDGE\", \"IE\", \"SAFARI\"."""

    auth_code_brower_timeout_seconds: int = 300
    """Seconds to wait before timing out when getting auth code from browser."""

    token_saving_method: TokenSavingMethod = TokenSavingMethod.KEYRING
    """What method to use for storing use auth tokens on the local machine. Possbile values: \"KEYRING\", \"IN_MEMORY\"."""

    # --- Testing ---
    test_user_id: Optional[str] = None
    """User ID for test user that will be used in integration tests. \n\n**Note:** Only used for development/testing."""

    test_user_auth_token: Optional[str] = None
    """Auth token for test user that will be used in integration tests. \n\n**Note:** Only used for development/testing.."""


anilist_settings = AnilistSettings()  # type: ignore
