import os
import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DEST_CHANNEL = int(os.environ.get("DEST_CHANNEL", "-1002301276562"))

app = Client("forwarder-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def clean_caption(caption: str) -> str:
    if not caption:
        return "provided by [Study Dimension](https://t.me/STUDY_DIMENSION_NETWORK)"
    caption = re.sub(r"https?://\S+", "https://t.me/STUDY_DIMENSION_NETWORK", caption)
    return f"{caption}\n\nprovided by [Study Dimension](https://t.me/STUDY_DIMENSION_NETWORK)"
@app.on_message(filters.command("copy") & filters.private)
async def copy_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Send a valid Telegram post link. For example:\n`/copy https://t.me/channel/10`")
        return

    try:
        input_link = message.command[1]
        match = re.match(r"https://t\.me/([^/]+)/(\d+)", input_link)
        if not match:
            await message.reply("❌ Invalid link format.")
            return

        source_channel = match[1]
        start_message_id = int(match[2])
        await message.reply(f"✅ Starting copy from `{source_channel}` at message ID {start_message_id}...")

        current_id = start_message_id
        success = 0

        while True:
            try:
                msg = await app.get_messages(source_channel, current_id)
                if not msg:
                    break
if msg.media:
                    await msg.copy(DEST_CHANNEL, caption=clean_caption(msg.caption or msg.text))
                else:
                    await app.send_message(DEST_CHANNEL, clean_caption(msg.text))

                success += 1
                current_id += 1
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"Stopped at {current_id} → {e}")
                break

        await message.reply(f"✅ {success} messages copied successfully.")

    except Exception as e:
        await message.reply(f"❌ Error occurred:\n`{str(e)}`")

app.run()
