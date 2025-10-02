from pydantic_settings import BaseSettings

class AnilistSettings(BaseSettings):
    # General
    anilist_api_url: str = "https://graphql.anilist.co"
    anilist_auth_url: str = "https://anilist.co/api/v2/oauth/authorize"
    anilist_token_url: str = "https://anilist.co/api/v2/oauth/token"

    # Auth
    anilist_client_id: str
    anilist_client_secret: str
    anilist_client_redirect_url: str

    class Config:
        env_file = ".env"
        extra = "ignore"


anilist_settings = AnilistSettings() # type: ignore
