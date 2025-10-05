import os
from pathlib import Path

from nifty_anilist.logging import anilist_logger as logger


DOTENV_PATH = Path("test/.env")


# Runs before all fixtures.
def pytest_configure(config):
    # Create a temporary .env file for tests.
    with open(DOTENV_PATH, "w"):
        pass


# Run before tests start.
def pytest_sessionstart(session):
    pass


# Runs after tests finish.
def pytest_sessionfinish(session, exitstatus):
    # Delete the temporary .env file for tests.
    if os.path.exists(DOTENV_PATH):
        os.remove(DOTENV_PATH)
    else:
        logger.error(f"Testing .env file not found on path {DOTENV_PATH}")


# Run on final teardown.
def pytest_unconfigure(config):
    pass
