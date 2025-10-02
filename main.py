import requests

from src.settings import anilist_settings
from src.util.auth import get_auth_token

if __name__ == "__main__":
    token = get_auth_token()

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
        "name": "AlexP"
    }

    response = requests.post(
        url=anilist_settings.anilist_api_url,
        headers= {
			'Authorization': 'Bearer ' + token,
			'Content-Type': 'application/json',
			'Accept': 'application/json',
		},
        json={"query": query, "variables": variables}
    )
    data = response.json()

    # Access the avatar URL
    avatar_url = data["data"]["User"]["avatar"]["large"]
    print("Avatar URL:", avatar_url)
