
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL = os.environ["CHANNEL_ID"]

HISTORY_FILE = Path("publicados.json")
SUBREDDITS = ["memes", "dankmemes"]

if HISTORY_FILE.exists():
    history = json.loads(HISTORY_FILE.read_text())
else:
    history = []

def get_reddit_posts(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=50"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "MemesDiarios/1.0"}
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read())["data"]["children"]

def publish(image_url, post_url):
    url = f"https://discord.com/api/v10/channels/{CHANNEL}/messages"
    data = json.dumps({
        "content": image_url + "\n" + post_url
    }).encode()

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bot {TOKEN}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        print("Meme publicado:", response.status)

for subreddit in SUBREDDITS:
    try:
        posts = get_reddit_posts(subreddit)

        for item in posts:
            post = item["data"]
            post_id = post["id"]
            image = post.get("url_overridden_by_dest", "")

            if (
                post_id not in history
                and post.get("post_hint") == "image"
                and image.lower().split("?")[0].endswith(
                    (".jpg", ".jpeg", ".png", ".gif")
                )
            ):
                publish(image, "https://reddit.com" + post["permalink"])
                history.append(post_id)
                HISTORY_FILE.write_text(
                    json.dumps(history[-500:])
                )
                raise SystemExit(0)

    except SystemExit:
        raise
    except Exception as error:
        print("Error en", subreddit, error)

raise SystemExit("No se encontró un meme nuevo con imagen.")
