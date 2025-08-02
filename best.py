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

# Regex to extract channel and message ID from Telegram link
LINK_REGEX = r"https:\/\/t\.me\/([a-zA-Z0-9_]+)/(\d+)"
@app.on_message(filters.command("startforward") & filters.private)
async def start_forwarding(client, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ Use like:\n`/startforward https://t.me/channel/123`")
        return

    match = re.match(LINK_REGEX, message.command[1])
    if not match:
        await message.reply("❌ Invalid link format.")
        return

    channel_username = match.group(1)
    msg_id = int(match.group(2))
    chat_id = message.chat.id

    active_tracking[chat_id] = (channel_username, msg_id)
    await message.reply(f"✅ Started copying from `{channel_username}` starting at message ID `{msg_id}`.")

    asyncio.create_task(forward_loop(chat_id))
async def forward_loop(chat_id):
    channel, msg_id = active_tracking[chat_id]

    while active_tracking.get(chat_id) == (channel, msg_id):
        try:
            msg = await app.get_messages(channel, msg_id)

            if msg and (msg.video or msg.audio or msg.document):
                caption_text = "Provided by [Study Dimension](https://t.me/STUDY_DIMENSION_NETWORK)"
                await app.copy_message(
                    chat_id=DEST_CHANNEL,
                    from_chat_id=channel,
                    message_id=msg_id,
                    caption=caption_text,
                    caption_entities=[
                        {
                            "type": "text_link",
                            "offset": 13,
                            "length": 15,
                            "url": "https://t.me/STUDY_DIMENSION_NETWORK"
                        }
                    ]
                )

            msg_id += 1
            active_tracking[chat_id] = (channel, msg_id)
            await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(5)


app.run()
