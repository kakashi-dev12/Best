import os
import re
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageIdInvalid, FloodWait

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Channel where to forward
DEST_CHANNEL = "bestum_best"
CUSTOM_CAPTION = "https://t.me/STUDY_DIMENSION_NETWORK"

app = Client("forwarder", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask app to keep Render alive
web = Flask(__name__)

@web.route('/')
def home():
    return "✅ Bot is alive!"

# Active forward tracking per user
active_tracking = {}

@app.on_message(filters.private & filters.text)
async def start_forwarding(client, message: Message):
    link = message.text.strip()
    match = re.match(r"https?://t\.me/([\w\d_]+)/(\d+)", link)

    if not match:
        await message.reply("❌ Invalid link. Use format:\nhttps://t.me/channelname/123")
        return

    channel_username, msg_id = match.groups()
    msg_id = int(msg_id) + 1

    chat_id = message.chat.id
    active_tracking[chat_id] = (channel_username, msg_id)
    await message.reply(f"✅ Started forwarding from `{channel_username}` after message `{msg_id - 1}`")

    asyncio.create_task(forward_loop(chat_id))
    async def forward_loop(chat_id):
    channel, msg_id = active_tracking[chat_id]

    while active_tracking.get(chat_id) == (channel, msg_id):
        try:
            msg = await app.get_messages(channel, msg_id)

            if msg.video or msg.audio or msg.document:
                await app.copy_message(
                    chat_id=DEST_CHANNEL,
                    from_chat_id=channel,
                    message_id=msg_id,
                    caption=CUSTOM_CAPTION if msg.caption or msg.text else None
                )

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

# Run Flask in background thread
def run_flask():
    web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app.run()
