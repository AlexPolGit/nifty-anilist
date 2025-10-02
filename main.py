import asyncio

from src.util.request import anilist_request

async def test_get_avatar():
    username = input('Username: ')

    query = """
        query GetUserAvatar($name: String) {
            User(name: $name) {
                avatar {
                    large
                }
            }
        }
    """

    variables = {
        "name": username
    }

    data = await anilist_request(query=query, variables=variables)

    # Access the avatar URL
    avatar_url = data["data"]["User"]["avatar"]["large"]
    print("Avatar URL:", avatar_url)

if __name__ == "__main__":
    asyncio.run(test_get_avatar())
