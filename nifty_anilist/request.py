from typing import Any, Dict, Optional
from gql import Client, GraphQLRequest
from gql.transport.aiohttp import AIOHTTPTransport

from nifty_anilist.utils.request_utils import create_request_headers, schema, run_request_with_retry
from nifty_anilist.settings import anilist_settings


async def anilist_request(query_request: GraphQLRequest, user_id: Optional[str] = None, use_auth: bool = True) -> Dict[str, Any]:
    """Make a request to the Anilist GraphQL API.
    This will include retrying if we are being rate limited.

    Args:
        query_request: GraphQL query to make to the API.
        user_id: ID of the user to use for authentiation. Leave empty to use the global user.
        use_auth: Whether to auth the auth header or not. Default is `True`.

    Returns:
        result: Result of the query, as a dictionary.
    """

    transport = AIOHTTPTransport(
        url=anilist_settings.api_url,
        headers=create_request_headers(user_id, use_auth)
    )

    client = Client(transport=transport, schema=schema())

    async with client as session:
        return await run_request_with_retry(session.execute(query_request))
