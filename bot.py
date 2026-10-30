import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL = os.environ["CHANNEL_ID"]
HISTORY = Path("publicados.json")
FEED = "https://jaidefinichon.com/feed/"

history = json.loads(HISTORY.read_text()) if HISTORY.exists() else []

def get_posts():
    req = urllib.request.Request(
        FEED,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        xml = response.read()

    root = ET.fromstring(xml)
    posts = []

    for item in root.findall(".//item"):
        link = item.findtext("link")
        title = item.findtext("title")
        description = item.findtext("description") or ""

        if link:
            posts.append({
                "link": link,
                "title": title or "Nuevo meme",
                "description": description
            })

    return posts

def publish(post):
    url = f"https://discord.com/api/v10/channels/{CHANNEL}/messages"

    payload = json.dumps({
        "content": f'**{post["title"]}**\n{post["link"]}'
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bot {TOKEN}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        print("Publicado:", response.status)

posts = get_posts()

for post in posts:
    if post["link"] not in history:
        publish(post)
        history.append(post["link"])
        HISTORY.write_text(json.dumps(history[-500:]))
        break
else:
    raise SystemExit("No hay publicaciones nuevas.")
