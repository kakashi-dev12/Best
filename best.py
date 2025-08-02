import os
import re
from pyrogram import Client, filters
from pyrogram.types import Message

# Load secrets
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Fixed destination channel ID (your channel)
DEST_CHANNEL_ID = 2301276562
CREDIT_TEXT = "provided by [study dimension](https://t.me/STUDY_DIMENSION_NETWORK)"

# Start bot
app = Client("forwarder_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
@app.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    await message.reply_text(
        "**Usage Instructions:**\n\n"
        "- Send any message link like:\n"
        "`https://t.me/channel_username/123`\n"
        "- The bot will forward all media messages starting from that ID.\n"
        "- Captions will be replaced with credit.",
        disable_web_page_preview=True
    )

@app.on_message(filters.regex(r"https://t\.me/[\w_]+/\d+"))
async def handle_link(client, message: Message):
    try:
        link = message.text
        match = re.search(r"https://t\.me/([\w_]+)/(\d+)", link)
        if not match:
            await message.reply("❌ Invalid link format.")
            return
        channel_username, msg_id = match.groups()
        msg_id = int(msg_id)
        current_id = msg_id
        success = 0
        while True:
            msg = await client.get_messages(channel_username, current_id)
            if not msg:
                break

            media = msg.photo or msg.video or msg.audio or msg.document
            caption = msg.caption or ""

            # Replace original links with credit
            caption = re.sub(r"https?://\S+", CREDIT_TEXT, caption)

            if media:
                await client.send_document(
                    chat_id=DEST_CHANNEL_ID,
                    document=media.file_id,
                    caption=caption,
                    parse_mode="markdown"
                )
                success += 1
            elif msg.text:
                await client.send_message(
                    chat_id=DEST_CHANNEL_ID,
                    text=re.sub(r"https?://\S+", CREDIT_TEXT, msg.text),
                    parse_mode="markdown"
                )
                success += 1

            current_id += 1  # Move to next message
        await message.reply(f"✅ Copied {success} messages from `{channel_username}`.")
    except Exception as e:
        await message.reply(f"❌ Error:\n{e}")

# Run the bot
app.run()
