import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

# env vars
PREFIX = os.getenv("PREFIX") or "!"
TOKEN = os.getenv("TOKEN")

# paths
EXTENSIONS = pathlib.Path("bot/exts/")

