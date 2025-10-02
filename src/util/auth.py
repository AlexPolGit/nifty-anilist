import requests
import json
import time
import urllib.parse as urlparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import jwt
from dotenv import get_key, set_key

from src.settings import anilist_settings

def get_auth_token() -> str:
    auth_token = get_key(".env", "ANILIST_AUTH_TOKEN")

    if auth_token is None or is_token_expired(auth_token):
        auth_code = get_auth_code_from_browser()
        auth_token = get_new_token(auth_code)
        set_key(".env", "ANILIST_AUTH_TOKEN", auth_token)

    return auth_token


def get_new_token(auth_code: str) -> str:
    resp = requests.post(anilist_settings.anilist_token_url,
        data={
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': anilist_settings.anilist_client_redirect_url
        },
        verify=False,
        allow_redirects=False,
        auth=(anilist_settings.anilist_client_id, anilist_settings.anilist_client_secret)
    )

    if resp.status_code != 200:
        raise Exception(f"AniList OAuth API gave {resp.status_code} response on auth code exchange with error: {resp.text}")

    resp_json = json.loads(resp.text)

    if 'access_token' not in resp_json:
        raise Exception('Access token missing from AniList OAuth response.')
    
    print("Aquired new auth token.")
    
    return resp_json['access_token']


def is_token_expired(token: str) -> bool:
    payload = jwt.decode(token, options={"verify_signature": False})
    exp = payload.get("exp")

    if exp is None or exp < time.time():
        print("Auth token is expired! Need to get a new one...")
        return True
    else:
        return False


def get_auth_code_from_browser() -> str:
    # Setup Chrome.
    driver = webdriver.Chrome()

    # Setup AniList OAuth URL.
    auth_url = f"{anilist_settings.anilist_auth_url}?" \
        f"client_id={anilist_settings.anilist_client_id}&" \
        f"redirect_uri={anilist_settings.anilist_client_redirect_url}&" \
        f"response_type=code"
    
    print(f"Opening auth page in Chrome: {auth_url}")
    
    # Open the page.
    driver.get(auth_url)

    # Wait for redirect to callback page with code.
    WebDriverWait(driver, 300).until(
        expected_conditions.url_contains(f"{anilist_settings.anilist_client_redirect_url}?code=")
    )

    # Extract the code from the URL
    parsed = urlparse.urlparse(driver.current_url)
    auth_code = urlparse.parse_qs(parsed.query).get("code", [None])[0]

    driver.quit()

    if auth_code is None:
        raise Exception("Failed to find an auth code from redirect URL.")

    return auth_code
