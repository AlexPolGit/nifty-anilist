from typing import Any, Optional
import httpx

from src.settings import anilist_settings
from src.util.auth import get_auth_token

async def anilist_request(query: str, variables: Optional[dict] = None) -> Any:
    token = get_auth_token()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=anilist_settings.anilist_api_url,
            headers= {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            json={"query": query, "variables": variables}
        )

        data = response.json()

        return data
