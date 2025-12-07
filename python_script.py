import os
import base64
import requests
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
IMAGES_FOLDER = os.getenv("IMAGES_FOLDER", "images")

api_id = 123456  # dummy, not used for bot
api_hash = "abc123abc123abc123abc123abc123"

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=BOT_TOKEN)

def upload_to_github(file_path, content, is_base64=False):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    if not is_base64:
        content = base64.b64encode(content.encode()).decode()
    data = {
        "message": f"Add {file_path}",
        "content": content,
        "branch": GITHUB_BRANCH
    }
    response = requests.put(url, json=data, headers=headers)
    print(response.status_code, response.json())

async def save_image(msg, post_id):
    if msg.media:
        file_name = f"{IMAGES_FOLDER}/post-{post_id}.jpg"
        path = await msg.download_media(file=file_name)
        with open(path, "rb") as f:
            img_data = f.read()
        upload_to_github(file_name, base64.b64encode(img_data).decode(), is_base64=True)
        return file_name
    return None

@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handler(event):
    msg = event.message
    post_id = msg.id
    
    # Upload image first (if exists)
    image_path = await save_image(msg, post_id)
    
    # Prepare Markdown content
    markdown = f"""---
title: "Telegram Post {post_id}"
date: "{msg.date}"
---

{msg.message if msg.message else ""}

"""
    if image_path:
        markdown += f"![Image]({image_path})\n"

    filename = f"posts/post-{post_id}.md"
    upload_to_github(filename, markdown)

print("Bot started and listening...")
client.run_until_disconnected()
