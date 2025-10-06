import asyncio

from nifty_anilist.client.custom_queries import Query
from nifty_anilist.client.custom_fields import UserFields, UserAvatarFields

from nifty_anilist import sign_in_if_no_global
from nifty_anilist import AnilistClient


async def test_get_avatar():
    """Simple test to get a user's avatar."""

    # Setup the global user if needed.
    sign_in_if_no_global()

    # Get username you want to see the avatar of.
    username = input("Username: ")

    async with AnilistClient() as client:
        query = Query.user(name=username).fields(
            UserFields.avatar().fields(UserAvatarFields.large)
        )

        response = await client.anilist_request(query)

        # Access the avatar URL.
        avatar_url = response["User"]["avatar"]["large"]
        print(f"Avatar URL: {avatar_url}")


if __name__ == "__main__":
    asyncio.run(test_get_avatar())
