from pathlib import Path
from pydantic_settings import BaseSettings


class AnilistSettings(BaseSettings):
    """Settings for Anilist-related things.
    Will be populated from environment variables or the local `.env` file.
    """

    # Configuration for the settings object.
    class Config:
        env_file = ".env"
        extra = "ignore"

    # General
    anilist_api_url: str = "https://graphql.anilist.co"
    anilist_auth_url: str = "https://anilist.co/api/v2/oauth/authorize"
    anilist_token_url: str = "https://anilist.co/api/v2/oauth/token"
    anilist_schema_path: str = "anilist_schema.graphql"

    # Auth
    anilist_client_id: str
    """Client ID from Anilist client.
    Reference: https://docs.anilist.co/guide/auth/#creating-an-application and https://anilist.co/settings/developer"""

    anilist_client_secret: str
    """Client secret from Anilist client.
    Reference: https://docs.anilist.co/guide/auth/#creating-an-application and https://anilist.co/settings/developer"""

    anilist_client_redirect_url: str
    """Client redirect URL from Anilist client.
    Reference: https://docs.anilist.co/guide/auth/#creating-an-application and https://anilist.co/settings/developer"""

    anilist_auth_code_brower_timeout_seconds: int = 300
    """Seconds to wait before timing out when getting auth code from browser."""

anilist_settings = AnilistSettings() # type: ignore
