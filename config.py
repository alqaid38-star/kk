import os
from os import getenv
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from OWNER import (
    BOT_TOKEN,
    OWNER,
    OWNER_ID,
    infophoto,
    OWNER_NAME,
    DATABASE,
    CHANNEL,
    GROUP,
    LOGS,
    PHOTO,
    VIDEO,
)


if os.path.exists("local.env"):
    load_dotenv("local.env")

load_dotenv()


admins = {}
user = {}
appp = {}
call = {}
logger = {}
logger_mode = {}
botname = {}
helper = {}


mo = AsyncIOMotorClient(DATABASE)     
moo = mo["data"]                      


Bots = moo["yousef"]
botdb = moo["botdb"]
blockdb = moo["blocked"]
db = moo

API_ID = int(getenv("API_ID", "17490746"))
API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")
BOT_TOKEN = BOT_TOKEN
MONGO_DB_URL = DATABASE
OWNER = OWNER
OWNER_ID = OWNER_ID
OWNER_NAME = OWNER_NAME
infophoto = infophoto
GROUP = GROUP
CHANNEL = CHANNEL
LOGS = LOGS
PHOTO = PHOTO
VIDEO = VIDEO