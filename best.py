import os
import asyncio
import re
from pyrogram import Client, filters

API_ID = int(os.environ.get("API_ID"))         # From https://my.telegram.org
API_HASH = os.environ.get("API_HASH")          # From https://my.telegram.org
BOT_TOKEN = os.environ.get("BOT_TOKEN")        # From @BotFather

# Replace with your channel ID (e.g., -1001234567890)
DEST_CHANNEL_ID = int(os.environ.get("DEST_CHANNEL_ID"))

app = Client("public_forward_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & filters.text)
async def forward_all_from_link(client, message):
    link = message.text.strip()
    match = re.match(r"https?://t\.me/([\w\d_]+)/(\d+)", link)

    if not match:
        await message.reply("❌ Please send a valid Telegram post link.\nExample:\nhttps://t.me/example_channel/534")
        return
    channel_username, msg_id = match.groups()
    msg_id = int(msg_id)

    await message.reply("⏳ Starting to forward messages...")

    count = 0
    while True:
        try:
            await client.copy_message(
                chat_id=DEST_CHANNEL_ID,
                from_chat_id=channel_username,
                message_id=msg_id
            )
            msg_id += 1
            count += 1
            await asyncio.sleep(0.5)  # delay to avoid FloodWait
        except Exception as e:
            if "message_id_invalid" in str(e).lower():
                break  # end reached
            elif "FLOOD" in str(e).upper():
                await asyncio.sleep(10)
                continue
            else:
                msg_id += 1  # skip missing/deleted
                continue

    await message.reply(f"✅ Done! Total {count} messages forwarded to your channel.")

app.run()
