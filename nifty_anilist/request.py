from typing import Any, Dict, Optional
from gql import GraphQLRequest

from nifty_anilist.utils.request_utils import create_client, run_request_with_retry


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

    client = create_client(user_id, use_auth)

    async with client as session:
        res = await session.execute(query_request)
        print(res)

    async with client as session:
        return await run_request_with_retry(session.execute(query_request))
