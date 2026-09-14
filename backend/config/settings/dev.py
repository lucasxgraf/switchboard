import os

from dotenv import load_dotenv

from .base import *

load_dotenv(BASE_DIR.parent / ".env")

DEBUG = True
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-key-local-only")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

API_KEY_HASH_SECRET = os.environ.get("API_KEY_HASH_SECRET", "dev-only-not-real")
