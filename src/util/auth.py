import time
import httpx
import urllib.parse as urlparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import jwt
from dotenv import get_key, set_key

from src.util.logging import anilist_logger as logger
from src.settings import anilist_settings


def get_auth_token() -> str:
    """Get auth token for Anilist requests. Required for any write operations.
    This token lasts 1 year and will be cached locally in the `.env` file.
    If the token does not exist in the `.env` file or is expired, this function will generate a new one.
    
    Returns:
        auth_token: An auth token valid that can be used in Anilist requests.
    """
    auth_token = get_key(".env", "ANILIST_AUTH_TOKEN")

    if auth_token is None or is_token_expired(auth_token):
        auth_code = get_auth_code_from_browser()
        auth_token = generate_new_token(auth_code)
        set_key(".env", "ANILIST_AUTH_TOKEN", auth_token)

    return auth_token


def generate_new_token(auth_code: str) -> str:
    """Generate a new Anilist auth token.
    This will call the Anilist auth token URL and request a new token based on the provided auth code.
    
    Args:
        auth_code: A short lived auth code from Anilist. See `get_auth_code_from_browser()`.

    Returns:
        token: An Anilist auth token that will last for 1 year.
    """
    response = httpx.post(
        url=anilist_settings.anilist_token_url,
        data={
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': anilist_settings.anilist_client_redirect_url
        },
        follow_redirects=False,
        auth=(anilist_settings.anilist_client_id, anilist_settings.anilist_client_secret)
    )

    response.raise_for_status()
    data = response.json()

    if 'access_token' not in data:
        raise Exception('Access token missing from AniList OAuth response.')
    
    logger.info("Aquired new auth token.")
    
    return data['access_token']


def is_token_expired(token: str) -> bool:
    """Checks if the given (JWT) auth token if expired or not.
    
    Args:
        token: JWT token, as a string.
        
    Returns:
        expired: `True` if the JWT token is expired, `False` otherwise.
    """
    payload = jwt.decode(token, options={"verify_signature": False})
    exp = payload.get("exp")

    if exp is None or exp < time.time():
        logger.warning("Auth token is expired! Need to get a new one...")
        return True
    else:
        return False


def get_auth_code_from_browser() -> str:
    """Uses a real Chrome browser to allow the user to manually sign into Anilist and then automatically retrieves their auth code.
    Might support other browsers later, idk.
        
    Returns:
        auth_code: Short-lived Anilist auth code that was grabbed from the browser.
    """
    # Setup Chrome.
    driver = webdriver.Chrome()

    # Setup AniList OAuth URL.
    auth_url = f"{anilist_settings.anilist_auth_url}?" \
        f"client_id={anilist_settings.anilist_client_id}&" \
        f"redirect_uri={anilist_settings.anilist_client_redirect_url}&" \
        f"response_type=code"
    
    logger.info(f"Opening auth page in Chrome: {auth_url}")
    
    # Open the page.
    driver.get(auth_url)

    # Wait for redirect to callback page with code.
    WebDriverWait(driver, anilist_settings.anilist_auth_code_brower_timeout_seconds).until(
        expected_conditions.url_contains(f"{anilist_settings.anilist_client_redirect_url}?code=")
    )

    # Extract the code from the URL
    parsed = urlparse.urlparse(driver.current_url)
    auth_code = urlparse.parse_qs(parsed.query).get("code", [None])[0]

    driver.quit()

    if auth_code is None:
        raise Exception("Failed to find an auth code from redirect URL.")

    return auth_code
