import asyncio

from nifty_anilist import AnilistClient, sign_in_if_no_global
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
from nifty_anilist.client.custom_queries import Query


async def test_get_avatar(username: str):
    """Simple test to get a user's avatar."""
    async with AnilistClient() as client:
        query = Query.user(name=username).fields(
            UserFields.avatar().fields(UserAvatarFields.large)
        )

        response = await client.anilist_request(query)

        # Access the avatar URL.
        avatar_url = response["User"]["avatar"]["large"]
        print(f"Avatar URL: {avatar_url}")


async def test_get_user_completed_anime_list(username: str):
    """Simple test to get all of a user's completed anime."""
    async with AnilistClient() as client:
        query = Query.media_list(
            user_name=username,
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
                    MediaTitleFields.native(),
                    MediaTitleFields.romaji(),
                )
            ),
        )

        response = await client.paginated_anilist_request(query)

        for anime in response:
            print(
                f"[{anime["mediaId"]}] {anime["media"]["title"]["native"]} ({anime["media"]["title"]["romaji"]}): {anime["score"]}/100"
            )


if __name__ == "__main__":
    # Setup the global user if needed.
    sign_in_if_no_global()

    # Get username of user to get info for.
    username = input("Username: ")

    asyncio.run(test_get_avatar(username))
    asyncio.run(test_get_user_completed_anime_list(username))
