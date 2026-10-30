
import json
import os
import urllib.request
from pathlib import Path

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL = os.environ["CHANNEL_ID"]
HISTORY = Path("publicados.json")

history = json.loads(HISTORY.read_text()) if HISTORY.exists() else []

def get_memes():
    url = "https://meme-api.com/gimme/20"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "MemesDiarios/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read()).get("memes", [])

def publish(meme):
    url = f"https://discord.com/api/v10/channels/{CHANNEL}/messages"

    payload = json.dumps({
        "content": meme["url"] + "\n" + meme["postLink"]
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
        print("Publicado correctamente:", response.status)

memes = get_memes()

for meme in memes:
    if meme.get("nsfw") or meme.get("spoiler"):
        continue

    post_id = meme.get("postLink")
    image = meme.get("url", "").lower().split("?")[0]

    if post_id and post_id not in history and image.endswith(
        (".jpg", ".jpeg", ".png", ".gif")
    ):
        publish(meme)
        history.append(post_id)
        HISTORY.write_text(json.dumps(history[-500:]))
        break
else:
    raise SystemExit("No se encontró un meme nuevo.")
