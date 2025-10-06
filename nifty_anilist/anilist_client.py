from typing import Any, Dict, Optional
import httpx

from nifty_anilist.settings import anilist_settings
from nifty_anilist.utils.auth_utils import UserId
from nifty_anilist.auth import get_auth_info
from nifty_anilist.utils.request_utils import run_request_with_retry
from nifty_anilist.client import Client
from nifty_anilist.client.custom_queries import GraphQLField

class AnilistClient:

    client: Client

    def __init__(self, user_id: Optional[UserId] = None, use_auth: bool = True) -> None:
        self.client = self._create_client(user_id, use_auth)

    def _create_client(self, user_id: Optional[UserId] = None, use_auth: bool = True) -> Client:
        """Create a client for Anilist requests.

        Args:
            user_id: ID of the user to use for authentiation. Leave empty to use the global user.
            use_auth: Whether to auth the auth header or not. Default is `True`.

        Returns:
            client: Custom GraphQL client for Anilist requests.
        """
        headers = self._create_request_headers(user_id, use_auth)

        client = Client(
            url=anilist_settings.api_url,
            headers=headers,
            http_client=httpx.AsyncClient(headers=headers, timeout=anilist_settings.request_timeout_seconds)
        )

        return client

    def _create_request_headers(self, user_id: Optional[UserId] = None, use_auth: bool = True) -> Dict[str, str]:
        """Create headers for an Anilist API request.

        Args:
            user_id: ID of the user to use for authentiation. Leave empty to use the global user.
            use_auth: Whether to auth the auth header or not. Default is `True`.

        Returns:
            headers: Appropriate headers for the API request based on the inputs.
        """
        headers: Dict[str, str] = {}

        if use_auth:
            auth_info = get_auth_info(user_id)
            headers["Authorization"] = f"Bearer {auth_info.token}"

        return headers

    async def anilist_request(self, query_request: GraphQLField, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Make a request to the Anilist GraphQL API.
        This will include retrying if we are being rate limited.

        Args:
            query_request: GraphQL query to make to the API.

        Returns:
            result: Result of the query, as a dictionary.
        """

        async with self.client as session:
            return await run_request_with_retry(session.query(query_request, operation_name=operation_name if operation_name else "anilist_query"))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
