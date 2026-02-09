import os
from os import getenv

API_ID = int(os.environ.get("API_ID", "31391448"))
API_HASH = os.environ.get("API_HASH", "e21bd3dd83341ec8f54a0b12d36bc039")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8539983744:AAFG1fPeqbgG6r3aP_nfFDtjZm9QMfmHF9w")

# Corrected line
BOT_USERNAME = os.environ.get("BOT_USERNAME", "ShaktimanXextractorbot")

OWNER_ID = int(os.environ.get("OWNER_ID", "7508714273"))
CREATOR_ID = int(os.environ.get("CREATOR_ID", "7508714273"))
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "-1003318044211"))

SUDO_USERS = list(map(int, getenv("SUDO_USERS", "5712470665").split()))

CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003721694802"))

# MongoDB check karein
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://nikhil:nikhil@cluster0.u5oypby.mongodb.net/?appName=Cluster0")

PREMIUM_LOGS = int(os.environ.get("PREMIUM_LOGS", "-1003709602892"))
