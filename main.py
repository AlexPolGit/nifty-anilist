import argparse

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
from nifty_anilist.prebuilt.media_list import get_user_media_list, UserMediaListFilters


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
    """Simple test to get all of a user's completed anime with a prebuilt function."""
    async with AnilistClient() as client:
        filters = UserMediaListFilters()
        filters.user_name = username
        filters.type = MediaType.ANIME
        filters.status_in = [MediaListStatus.COMPLETED]
        anile_list = await get_user_media_list(client, filters)

        for anime in anile_list:
            print(
                f"[{anime.mediaId}] {anime.media.title.native} ({anime.media.title.romaji}): {anime.score}/100"
            )


async def test_get_user_completed_anime_list_manual(username: str):
    """Simple test to get all of a user's completed anime manually."""
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
    # Get input arguments.
    parser = argparse.ArgumentParser(
        description="Demo main function for the Nifty Anilist Tools library."
    )
    parser.add_argument(
        "--get-avatar",
        dest="avatar",
        action="store_true",
        help='Enable the "test_get_avatar" test.',
    )
    parser.add_argument(
        "--get-user-completed-anime-list",
        dest="anime_list",
        action="store_true",
        help='Enable the "test_get_avatar" test.',
    )
    parser.add_argument(
        "--get-user-completed-anime-list-manual",
        dest="anime_list_manual",
        action="store_true",
        help='Enable the "test_get_avatar" test.',
    )
    args = parser.parse_args()

    # Setup the global user if needed.
    sign_in_if_no_global()

    # Get username of user to get info for.
    username = input("Username: ")

    # Run tests depending on input arguments.
    if args.avatar:
        asyncio.run(test_get_avatar(username))

    if args.anime_list:
        asyncio.run(test_get_user_completed_anime_list(username))

    if args.anime_list_manual:
        asyncio.run(test_get_user_completed_anime_list_manual(username))
