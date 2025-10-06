from typing import Any, Dict, Optional, Union, Coroutine
from collections import deque
from time import time
from http import HTTPStatus
import asyncio

from nifty_anilist.settings import anilist_settings
from nifty_anilist.logging import anilist_logger as logger
from nifty_anilist.client.exceptions import GraphQLClientHttpError


class RateLimitException(Exception):
    """Custom error to be thrown when we hit our internal rate limit."""

    pass


async def run_request_with_retry(
    api_request_function: Coroutine[Any, Any, Dict[str, Any]],
) -> Dict[str, Any]:
    """Function for running an async Anilist API request and retrying if a rate limit error happens.

    Args:
        api_request_function: Anilist API request function that returns the API result.

    Returns:
        response: Response from the Anilist API.
    """
    max_attempts: Optional[int] = anilist_settings.rate_limit_max_retries
    initial_delay: Optional[int] = anilist_settings.rate_limit_retry_initial_delay
    max_requests_per_minute: Optional[int] = anilist_settings.max_requests_per_minute

    for attempt in attempt_iterator(max_attempts):
        try:
            # If we are manually tracking requests and reach the max requests per minute, throw "RateLimitException".
            # The sleep_for_rate_limit() function will know what to do with it.
            if max_requests_per_minute:
                # Check how many requests were made in the last minute.
                request_count = get_request_count_last_minute()

                if request_count >= max_requests_per_minute:
                    raise RateLimitException()

            # Run the API request.
            result = await api_request_function

            # Track the request count.
            await record_request()

            return result

        except RateLimitException as e:
            await sleep_for_rate_limit(initial_delay, attempt, max_attempts, e)

        except GraphQLClientHttpError as e:
            if e.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                await sleep_for_rate_limit(initial_delay, attempt, max_attempts, e)
            else:
                raise

    raise RuntimeError("Failed to complete request.")


async def sleep_for_rate_limit(
    initial_delay: Optional[int],
    attempt: int,
    max_attempts: Optional[int],
    error: Union[RateLimitException, GraphQLClientHttpError],
):
    """Function to sleep after a rate limit was imposed on our API calls.

    Args:
        initial_delay: Initial amount of seconds to wait after getting rate limited.
        attempt: Current attempt number.
        max_attempts: Max number of attempts to make.
        error: Error that caused this sleep attempt. "RateLimitException" = from internal rate limiter. "GraphQLClientHttpError" = rate limit error from API.
    """
    if attempt == max_attempts:
        raise RuntimeError(
            f"Could not complete request after {max_attempts} attempts."
        ) from error

    delay: int

    # Expect "RateLimitException" to be thrown by our own rate limiter.
    if isinstance(error, RateLimitException):
        # If the initial delay was provided, use it and increment by 5 seconds every time.
        if initial_delay:
            delay = initial_delay if attempt == 1 else (attempt * 2)
        # Otherwise wait just over 1 minute and increment by 5 seconds every time.
        else:
            delay = 61 if attempt == 1 else (attempt * 2)

    # Expect "TransportServerError" to be thrown when we get rate limited by the Anilist API.
    else:
        # If the initial delay was provided, use it and increment by 5 seconds every time.
        if initial_delay:
            delay = initial_delay if attempt == 1 else (attempt * 2)
        # Otherise try to retrieve the recommended delay from response headers.
        else:
            base_error = error.__cause__
            if isinstance(base_error, GraphQLClientHttpError):
                error_headers = base_error.response.headers
                retry_after = error_headers["Retry-After"] if error_headers else None
                if retry_after:
                    delay = int(retry_after)
                else:
                    raise RuntimeError(
                        'Could not find "Retry-After" header in rate limit response.'
                    ) from error
            else:
                raise RuntimeError(
                    "Could not extract base error from TransportServerError."
                ) from error

    logger.warning(f"Retrying due to rate limit error in {delay}s (attempt {attempt}).")
    await asyncio.sleep(delay)


def attempt_iterator(max_attempts: Optional[int] = None):
    """Iterator that will incrementally generate integers until a max value, if specified.

    Args:
        max_attempts: Largest integer that can be generated.
    """
    attempt = 1
    while max_attempts is None or attempt <= max_attempts:
        yield attempt
        attempt += 1


# ------------------------- Local request counter (rate limiter) that is used if a max requests per minute is set in the settings. -----

REQUEST_COUNTER_LOCK: asyncio.Lock = asyncio.Lock()
"""Global lock for interacting with the attempt recorder."""

REQUEST_COUNTER: deque[float] = deque()
"""Sliding request counter that holds all the API call attempts made in the last minute."""


async def record_request() -> int:
    """Record an Anilist API request attemp.

    Returns:
        attempts: Number of attempts in the last minute.
    """
    async with REQUEST_COUNTER_LOCK:
        now = time()
        REQUEST_COUNTER.append(now)

        # Remove timestamps older than 60 seconds
        while now - REQUEST_COUNTER[0] > 60:
            REQUEST_COUNTER.popleft()

        return get_request_count_last_minute()


def get_request_count_last_minute():
    """Get the number of Anilist API requests made in the last minute."""
    return len(REQUEST_COUNTER)


async def reset_request_counter():
    """Reset the request counter."""
    async with REQUEST_COUNTER_LOCK:
        REQUEST_COUNTER.clear()
