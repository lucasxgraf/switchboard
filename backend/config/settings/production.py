import os

from .base import *

DEBUG = False

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

API_KEY_HASH_SECRET = os.environ["API_KEY_HASH_SECRET"]
