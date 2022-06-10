"""Reads settings from environment variables and sets default values.

Local development:
  bot-0-action-server/.env

GitHub CI/CD:
  Define as repository secrets in GitHub repository, under Settings

Production deployment as Digital Ocean App:
  Define as environment variables in DO App's Dashboard, under Settings

"""
from pathlib import Path
from typing import cast
from pydantic import BaseSettings, AnyHttpUrl

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


class SettingsFromEnvironment(BaseSettings):
    """Defines environment variables with their types and optional defaults"""

    DEBUG: bool = False
    SECRET_JWT_KEY: str
    JWT_METHOD: str = "HS256"
    BOT_0_ACTION_SERVER_IC_IDENTITY_PEM_ENCODED: str
    # https://github.com/rocklabs-io/ic-py/issues/25
    IC_NETWORK_URL: AnyHttpUrl = cast(AnyHttpUrl, "http://localhost:8000")

    CANISTER_MOTOKO_ID: str
    CANISTER_MOTOKO_CANDID_UI: AnyHttpUrl

    class Config:  # pylint: disable=too-few-public-methods
        """Defines configuration for pydantic environment loading"""

        env_file = str(BASE_DIR / ".env")
        case_sensitive = True


config = SettingsFromEnvironment()

DEBUG = config.DEBUG
SECRET_JWT_KEY = config.SECRET_JWT_KEY
JWT_METHOD = config.JWT_METHOD
BOT_0_ACTION_SERVER_IC_IDENTITY_PEM_ENCODED = (
    config.BOT_0_ACTION_SERVER_IC_IDENTITY_PEM_ENCODED
)
IC_NETWORK_URL = config.IC_NETWORK_URL
CANISTER_MOTOKO_ID = config.CANISTER_MOTOKO_ID
CANISTER_MOTOKO_CANDID_UI = config.CANISTER_MOTOKO_CANDID_UI
