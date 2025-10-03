import asyncio
from gql import gql

from src.util.logging import anilist_logger as logger
from src.util.auth import get_auth_token
from src.util.request import anilist_request

async def test_get_avatar():
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

    data = await anilist_request(query_request=query)

    # Access the avatar URL
    avatar_url = data["User"]["avatar"]["large"]
    logger.info(f"Avatar URL: {avatar_url}")


if __name__ == "__main__":
    _ = get_auth_token()
    asyncio.run(test_get_avatar())
