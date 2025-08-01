import os
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageIdInvalid, FloodWait

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ✅ SET YOUR CHANNEL USERNAME (destination)
MY_CHANNEL = "https://t.me/bestie_best"   # ← Change this (without @)

# ✅ CUSTOM NAME TO SHOW WITH FORWARDED MEDIA
CUSTOM_CAPTION = "📦 From: @STUDY_DIMENSION_NETWORK"

app = Client("public_forward_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Track active sessions per user
active_tracking = {}

@app.on_message(filters.private & filters.text)
async def start_tracking(client, message: Message):
    link = message.text.strip()
    match = re.match(r"https?://t\.me/([\w\d_]+)/(\d+)", link)

    if not match:
        await message.reply("❌ Invalid link. Use format like:\nhttps://t.me/channelname/123")
        return
channel_username, msg_id = match.groups()
    msg_id = int(msg_id) + 1  # Start after given message

    chat_id = message.chat.id
    active_tracking[chat_id] = (channel_username, msg_id)
    await message.reply(f"✅ Forwarding started from `{channel_username}` after message `{msg_id - 1}`")

    asyncio.create_task(forward_media(chat_id))

async def forward_media(chat_id):
    channel, msg_id = active_tracking[chat_id]

    while active_tracking.get(chat_id) == (channel, msg_id):
        try:
            msg = await app.get_messages(channel, msg_id)

            if msg.video or msg.audio:
                caption = CUSTOM_CAPTION
                await app.copy_message(chat_id=MY_CHANNEL, from_chat_id=channel, message_id=msg_id, caption=caption)
                await asyncio.sleep(1)

            msg_id += 1
            active_tracking[chat_id] = (channel, msg_id)
            await asyncio.sleep(2)

        except MessageIdInvalid:
            await asyncio.sleep(5)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception as e:
            await app.send_message(chat_id, f"⚠️ Error while forwarding:\n`{e}`")
            await asyncio.sleep(10)

app.run()
