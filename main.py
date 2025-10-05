import asyncio
from gql import gql

from nifty_anilist.logging import anilist_logger as logger
from nifty_anilist.auth import sign_in_if_no_global
from nifty_anilist.client import AnilistClient


async def test_get_avatar():
    """Simple test to get a user's avatar."""

    # Setup the global user if needed.
    sign_in_if_no_global()

    # Get username you want to see the avatar of.
    username = input('Username: ')

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
        "name": username
    }

    async with AnilistClient() as client:
        # Do query with global user.
        data = await client.anilist_request(query_request=query)

        # Access the avatar URL.
        avatar_url = data["User"]["avatar"]["large"]
        logger.info(f"Avatar URL: {avatar_url}")


if __name__ == "__main__":
    asyncio.run(test_get_avatar())
