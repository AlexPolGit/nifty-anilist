from typing import Any, Dict, Optional, Union, List
import httpx

from nifty_anilist.settings import anilist_settings
from nifty_anilist.logging import anilist_logger as logger
from nifty_anilist.utils.auth_utils import UserId
from nifty_anilist.auth import get_auth_info
from nifty_anilist.utils.request_utils import run_request_with_retry
from nifty_anilist.client import Client
from nifty_anilist.client.custom_queries import Query
from nifty_anilist.client.custom_fields import PageInfoFields
from nifty_anilist.client.custom_queries import (
    GraphQLField,
    PageFields,
    ActivityReplyFields,
    ActivityUnionUnion,
    AiringScheduleFields,
    CharacterFields,
    MediaFields,
    MediaListFields,
    MediaTrendFields,
    NotificationUnionUnion,
    RecommendationFields,
    ReviewFields,
    StaffFields,
    StudioFields,
    ThreadCommentFields,
    ThreadFields,
    UserFields,
)


class AnilistClient:

    client: Client

    def __init__(self, user_id: Optional[UserId] = None, use_auth: bool = True) -> None:
        self.client = self._create_client(user_id, use_auth)

    def _create_client(
        self, user_id: Optional[UserId] = None, use_auth: bool = True
    ) -> Client:
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
            http_client=httpx.AsyncClient(
                headers=headers, timeout=anilist_settings.request_timeout_seconds
            ),
        )

        return client

    def _create_request_headers(
        self, user_id: Optional[UserId] = None, use_auth: bool = True
    ) -> Dict[str, str]:
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

    async def anilist_request(
        self, query_request: GraphQLField, operation_name: str = "anilist_query"
    ) -> Dict[str, Any]:
        """Make a request to the Anilist GraphQL API.
        This will include retrying if we are being rate limited.

        Args:
            query_request: GraphQL query to make to the API.
                This can be done with `Query.{field_name}( … ).fields( … )`.
            operation_name: Name of the GraphQL operation.
                This can pretty much be anything since we are only making one request at a time.

        Returns:
            result: Result of the query, as a dictionary.
        """

        return await run_request_with_retry(
            lambda: self.client.query(
                query_request,
                operation_name=operation_name,
            )
        )

    async def paginated_anilist_request(
        self,
        query_request: Union[
            ActivityReplyFields,
            ActivityUnionUnion,
            AiringScheduleFields,
            CharacterFields,
            MediaFields,
            MediaListFields,
            MediaTrendFields,
            NotificationUnionUnion,
            RecommendationFields,
            ReviewFields,
            StaffFields,
            StudioFields,
            ThreadCommentFields,
            ThreadFields,
            UserFields,
        ],
        starting_page: int = 1,
        per_page: int = 50,
        operation_name: str = "paginated_anilist_query",
    ) -> List[Any]:
        """Make a paginated request to the Anilist GraphQL API.
        This method abstracts away pagination logic and lets you just input the request for the fields you want.
        This will include retrying if we are being rate limited.

        Args:
            query_request: GraphQL query to make to the API.
                This can be done with `PageFields.{field_name}( … ).fields( … )` (recommended) or `Query.{field_name}( … ).fields( … )`.
            starting_page: Page to start the pagination from. **Note:** The API is 1-indexed, so the first page is not 0.
            per_page: Items to return per page (request). 50 is generally the maximum amount.
                **Note:** Entering a value above the max should not throw an error but just return the max amount.
            operation_name: Name of the GraphQL operation.
                This can pretty much be anything since we are only making one request at a time.

        Returns:
            result: Result of the query, as a list of all the objects retrieved from the API.
        """

        # If the user's "query_request" object was generated with Query.{field_name}(), the field name will be wrong (title case instead of camel case).
        # Fix this here just in case it happens.
        # This doesn't happen if the "query_request" object is generated with PageFields.{field_name}(), but might as well do a small hack instead of enforcing that approach.
        query_request._field_name = (
            query_request._field_name[0].lower() + query_request._field_name[1:]
        )

        results = []
        has_next = True
        page = starting_page

        while has_next:
            logger.info(
                f"[{query_request._field_name}] Getting page {page} of paginated request."
            )

            query = Query.page(page=page, per_page=per_page).fields(
                PageFields.page_info().fields(PageInfoFields.has_next_page),
                query_request,
            )

            paginated_result = await self.anilist_request(query, operation_name)
            results.extend(paginated_result["Page"][query_request._field_name])

            has_next = bool(paginated_result["Page"]["pageInfo"]["hasNextPage"])
            page += 1

        return results

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
