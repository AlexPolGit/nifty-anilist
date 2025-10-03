from typing import Optional, Dict
import time
import httpx
import urllib.parse as urlparse
import keyring
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import jwt

from nifty_anilist.logging import anilist_logger as logger
from nifty_anilist.settings import anilist_settings, TokenSavingMethod


KEYRING_SERVICE_NAME = "nifty-anilist-python"


IN_MEMORY_TOKEN_STORAGE: Dict[str, str] = {}


def save_token(user_id: str, token: str) -> None:
    """Save an auth token locally.
    
    Args:
        user_id: ID of the user to save the token for.
        token: The value of the token to save.
    """
    if (anilist_settings.token_saving_method == TokenSavingMethod.KEYRING):
        keyring.set_password(KEYRING_SERVICE_NAME, user_id, token)
    elif (anilist_settings.token_saving_method == TokenSavingMethod.IN_MEMORY):
        IN_MEMORY_TOKEN_STORAGE[user_id] = token
    else:
        raise Exception("Unknown token storage method.")


def get_token(user_id: str) -> Optional[str]:
    """Get the auth token stored locally for a user.
    
    Args:
        user_id: ID of the user to get the token for.
    """
    if (anilist_settings.token_saving_method == TokenSavingMethod.KEYRING):
        return keyring.get_password(KEYRING_SERVICE_NAME, user_id)
    elif (anilist_settings.token_saving_method == TokenSavingMethod.IN_MEMORY):
        return IN_MEMORY_TOKEN_STORAGE[user_id]
    else:
        raise Exception("Unknown token storage method.")


def delete_token(user_id: str) -> None:
    """Delete a local auth token.
    
    Args:
        user_id: ID of the user to delete the token for.
    """
    if (anilist_settings.token_saving_method == TokenSavingMethod.KEYRING):
        keyring.delete_password(KEYRING_SERVICE_NAME, user_id)
    elif (anilist_settings.token_saving_method == TokenSavingMethod.IN_MEMORY):
        try:
            IN_MEMORY_TOKEN_STORAGE.pop(user_id)
        except KeyError:
            pass
        except:
            raise
    else:
        raise Exception("Unknown token storage method.")


def generate_new_token() -> str:
    """Generate a new Anilist auth token.
    This will call the Anilist auth token URL and request a new token based on the provided auth code.
    
    Args:
        auth_code: A short lived auth code from Anilist. See `get_auth_code_from_browser()`.

    Returns:
        token: An Anilist auth token that will last for 1 year.
    """
    # Get new auth code from browser.
    auth_code = get_auth_code_from_browser()
    
    # Send auth code to Anilist's token endpoint.
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


def get_user_from_token(token: str) -> str:
    """Get the Anilist user ID from a given (JWT) auth token.
    
    Args:
        token: JWT token, as a string.
        
    Returns:
        user_id: ID of the Anilist user in the JWT token.
    """
    payload = jwt.decode(token, options={"verify_signature": False})
    sub = payload.get("sub")

    if sub is None or not isinstance(sub, str):
        raise Exception("User not found in auth token!")
    else:
        return sub


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


def open_credential_manager():
    """Open the credential manager for debugging purposes. **Note:** Only works on Windows."""
    import platform
    import subprocess

    if platform.system() == "Windows":
        subprocess.run(["control", "/name", "Microsoft.CredentialManager"])
    else:
        raise Exception("This function only supports Windows for now.")
