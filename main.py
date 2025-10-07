import argparse

import asyncio
from datetime import datetime, timedelta

from nifty_anilist import AnilistClient, sign_in_if_no_global
from nifty_anilist.client.custom_fields import (
    MediaFields,
    MediaListFields,
    MediaListSort,
    MediaListStatus,
    MediaSort,
    MediaStatus,
    MediaTitleFields,
    MediaType,
    ScoreFormat,
    UserAvatarFields,
    UserFields,
)
from nifty_anilist.client.custom_queries import Query
from nifty_anilist.prebuilt import get_media_list, MediaListFilters, get_user_media_list, UserMediaListFilters


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
    """Test to get all of a user's completed anime with a prebuilt function."""
    async with AnilistClient() as client:
        filters = UserMediaListFilters(
            type=MediaType.ANIME, status_in=[MediaListStatus.COMPLETED]
        )
        anime_list = await get_user_media_list(
            client, user_name=username, list_filters=filters
        )

        for anime in anime_list:
            print(
                f"[{anime.mediaId}] {anime.media.title.native} ({anime.media.title.romaji}): {anime.score}/100"
            )


async def test_get_recent_anime():
    """Test to get some recently aired (completed) anime with a prebuilt function."""
    async with AnilistClient() as client:
        one_year_ago = datetime.today() - timedelta(days=365)
        fuzz_date = int(one_year_ago.strftime("%Y%m%d"))

        filters = MediaListFilters(
            type=MediaType.ANIME,
            status_in=[MediaStatus.FINISHED],
            start_date_greater=fuzz_date,
        )
        anime_list = await get_media_list(client, list_filters=filters)

        for anime in anime_list:
            print(
                f"[{anime.id}] {anime.title.native} ({anime.title.romaji}): {anime.meanScore}/100"
            )


async def test_get_popular_manga():
    """Test to get the most popular completed manga with a prebuilt function."""
    async with AnilistClient() as client:
        filters = MediaListFilters(
            type=MediaType.MANGA, sort=[MediaSort.SCORE_DESC], max_media_count=100
        )
        manga_list = await get_media_list(client, list_filters=filters)

        for manga in manga_list:
            print(
                f"[{manga.id}] {manga.title.native} ({manga.title.romaji}): {manga.meanScore}/100"
            )


async def test_get_user_completed_anime_list_manual(username: str):
    """Test to get all of a user's completed anime manually."""
    async with AnilistClient() as client:
        query = Query.media_list(
            user_name=username,
            type=MediaType.ANIME,
            status_in=[MediaListStatus.COMPLETED],
            sort=[MediaListSort.MEDIA_TITLE_NATIVE, MediaListSort.MEDIA_ID],
        ).fields(
            MediaListFields.media_id,
            MediaListFields.score(format=ScoreFormat.POINT_100),
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
        help='Run the "test_get_avatar" test.',
    )
    parser.add_argument(
        "--get-recent-anime",
        dest="get_recent_anime",
        action="store_true",
        help='Run the "get_recent_anime" test.',
    )
    parser.add_argument(
        "--get-popular-manga",
        dest="get_popular_manga",
        action="store_true",
        help='Run the "get_popular_manga" test.',
    )
    parser.add_argument(
        "--get-user-completed-anime-list",
        dest="anime_list",
        action="store_true",
        help='Run the "test_get_avatar" test.',
    )
    parser.add_argument(
        "--get-user-completed-anime-list-manual",
        dest="anime_list_manual",
        action="store_true",
        help='Run the "test_get_avatar" test.',
    )
    args = parser.parse_args()

    # Setup the global user if needed.
    sign_in_if_no_global()

    # Get username of user to get info for.
    username: str | None = None

    # Run tests depending on input arguments.
    if args.avatar:
        if username is None:
            username = input("Username: ")
        asyncio.run(test_get_avatar(username))

    if args.anime_list:
        if username is None:
            username = input("Username: ")
        asyncio.run(test_get_user_completed_anime_list(username))

    if args.get_recent_anime:
        asyncio.run(test_get_recent_anime())

    if args.get_popular_manga:
        asyncio.run(test_get_popular_manga())

    if args.anime_list_manual:
        if username is None:
            username = input("Username: ")
        asyncio.run(test_get_user_completed_anime_list_manual(username))
