import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import re

# Get values from Render environment
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DEST_CHANNEL = os.environ.get("DEST_CHANNEL")  # Example: -100xxxxxxxxxx

# Bot client
app = Client("forwarder_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Track active forwarding tasks per user
active_tracking = {}

# Regex to extrel and messom Telegram link
