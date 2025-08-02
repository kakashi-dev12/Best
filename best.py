import re
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DESTINATION_CHANNEL = int(os.environ.get("DEST_CHANNEL_ID"))

CUSTOM_LINK = "[Study Dimension](https://t.me/STUDY_DIMENSION_NETWORK)"

app = Client("forward_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def replace_links_and_add_credit(caption):
    if not caption:
        caption = ""
    caption = re.sub(r'https?://\S+', '', caption)
    caption += f"\n\nProvided by {CUSTOM_LINK}"
    return caption.strip()
@app.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply_text(
        "👋 Hello! Send me a public post link like:\n\n"
        "`https://t.me/channel_name/123`\n\n"
        "I'll copy all messages from that post to the latest and send them to your channel."
    )

@app.on_message(filters.command("help"))
async def help_cmd(_, msg: Message):
    await msg.reply_text(
        "🛠 **How to use:**\n\n"
        "Just send a message link like:\n"
        "`https://t.me/channel/5`\n\n"
        "I'll forward all messages from there to the latest and edit captions to include Study Dimension credit."
    )
@app.on_message(filters.regex(r"https://t\.me/[\w_]+/\d+"))
async def handle_link(_, msg: Message):
    try:
        link = msg.text.strip()
        parts = link.split("/")
        channel_username = parts[3]
        start_id = int(parts[4])

        await msg.reply_text(f"✅ Starting to forward from `{channel_username}` at ID {start_id}...")

        current_id = start_id
        while True:
            try:
                message = await app.get_messages(channel_username, current_id)
                if not message:
                    break

                caption = replace_links_and_add_credit(getattr(message, "caption", ""))

                if message.photo:
                    await app.send_photo(DESTINATION_CHANNEL, message.photo.file_id, caption=caption)
                elif message.video:
                    await app.send_video(DESTINATION_CHANNEL, message.video.file_id, caption=caption)
                elif message.document:
                    await app.send_document(DESTINATION_CHANNEL, message.document.file_id, caption=caption)
                elif message.audio:
                    await app.send_audio(DESTINATION_CHANNEL, message.audio.file_id, caption=caption)
                elif message.text:
                    await app.send_message(DESTINATION_CHANNEL, text=replace_links_and_add_credit(message.text))

                current_id += 1
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"❌ Error on message {current_id}: {e}")
                current_id += 1
                continue
            
            except Exception as e:
        await msg.reply_text(f"❌ Failed to start:\n{e}")

print("🤖 Bot is running and ready to copy posts!")
app.run()
