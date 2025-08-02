import os
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Fill these with your values
API_ID = int(os.environ.get("API_ID", 123456))  # Replace with your API_ID
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

DEST_CHANNEL = -1002301276562  # Your channel ID: bestum_best

app = Client("forwarder", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Clean caption and append your credit
def clean_caption(caption: str) -> str:
    if not caption:
        return "provided by [study dimension](https://t.me/STUDY_DIMENSION_NETWORK)"
    
    # Remove all links
    caption = re.sub(r'https?://\S+', '', caption)
    return caption.strip() + "\n\nprovided by [study dimension](https://t.me/STUDY_DIMENSION_NETWORK)"

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply("Send me the command in format:\n\n`channel/@channelusername/50/100`")

@app.on_message(filters.text & filters.private)
async def forward_range(_, message: Message):
    try:
        parts = message.text.strip().split("/")
        if len(parts) != 4 or not parts[2].isdigit() or not parts[3].isdigit():
            await message.reply("❌ Invalid format.\nUse like this:\n`channel/@channelusername/50/100`")
            return

        source_channel = parts[1]  # e.g., @channelusername
        start_id = int(parts[2])
        end_id = int(parts[3])

        success = 0
        current_id = start_id

        while current_id <= end_id:
            try:
                # Message fetch and forward block continues below...
                msg = await app.get_messages(source_channel, current_id)
                if not msg:
                    current_id += 1
                    continue

                if msg.media:
                    await msg.copy(DEST_CHANNEL, caption=clean_caption(msg.caption or msg.text))
                else:
                    await app.send_message(DEST_CHANNEL, clean_caption(msg.text or ""))

                success += 1
                await asyncio.sleep(0.5)
                current_id += 1

            except Exception as e:
                print(f"Error at message {current_id}: {e}")
                current_id += 1
                continue

        await message.reply(f"✅ Successfully copied {success} messages to your channel.")

    except Exception as e:
        await message.reply(f"❌ Error: `{str(e)}`")

app.run()
