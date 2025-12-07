import os
import time
import base64
import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH")
IMAGES_FOLDER = "images"
POSTS_FOLDER = "posts"

bot = Bot(token=BOT_TOKEN)

def upload_to_github(file_path, content, is_binary=False):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    if is_binary:
        content = base64.b64encode(content).decode()
    else:
        content = base64.b64encode(content.encode()).decode()

    data = {
        "message": f"Add {file_path}",
        "content": content,
        "branch": GITHUB_BRANCH
    }

    res = requests.put(url, json=data, headers=headers)
    print("GitHub:", res.status_code, res.text)

def handle_message(message):
    post_id = message.message_id
    text = message.text or ""

    image_path = None
    if message.photo:
        file_id = message.photo[-1].file_id
        file = bot.get_file(file_id)
        
        local_name = f"{IMAGES_FOLDER}/post-{post_id}.jpg"
        file.download(custom_path=local_name)

        with open(local_name, "rb") as f:
            img_data = f.read()

        github_img_path = f"{IMAGES_FOLDER}/post-{post_id}.jpg"
        upload_to_github(github_img_path, img_data, is_binary=True)
        image_path = github_img_path

    markdown = f"""---
title: "Telegram Post {post_id}"
date: "{message.date}"
---

# Telegram Post {post_id}

{text}

"""

    if image_path:
        markdown += f"![Image]({image_path})\n"

    github_md_path = f"{POSTS_FOLDER}/post-{post_id}.md"
    upload_to_github(github_md_path, markdown)

def start_bot():
    print("Bot started… checking for new messages every 2 sec")
    offset = None

    while True:
        updates = bot.get_updates(offset=offset, timeout=10)

        for update in updates:
            if update.channel_post:
                handle_message(update.channel_post)

            offset = update.update_id + 1

        time.sleep(2)

if __name__ == "__main__":
    start_bot()
