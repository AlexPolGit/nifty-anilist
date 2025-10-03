from typing import Any, Dict
from importlib.resources import files, as_file
from gql import Client, GraphQLRequest
from gql.transport.aiohttp import AIOHTTPTransport

from nifty_anilist.settings import anilist_settings
from nifty_anilist.auth import get_auth_token


def schema() -> str:
    """Get the Anilist API GraphQL schema.
    Will get the schema from local files.
    
    Returns:
        schema_string: Anilist API GraphQL schema as a string.
    """
    schema_resource = files(f"nifty_anilist").joinpath(anilist_settings.anilist_schema_path)

    with as_file(schema_resource) as path:
        with open(path, "r") as f:
            schema_string = f.read()
            return schema_string


async def anilist_request(query_request: GraphQLRequest, use_athh: bool = True) -> Dict[str, Any]:
    """Make a request to the Anilist GraphQL API.

    Args:
        query_request: GraphQL query to make to the API.
        use_auth: Whether to auth the auth header or not. Default is `True`.

    Returns:
        result: Result of the query, as a dictionary.
    """

    headers = {}

    if use_athh:
        token = get_auth_token()
        headers["Authorization"] = f"Bearer {token}"

    transport = AIOHTTPTransport(
        url=anilist_settings.anilist_api_url,
        headers=headers
    )

    client = Client(transport=transport, schema=schema())

    async with client as session:
        result = await session.execute(query_request)
        
        return result
