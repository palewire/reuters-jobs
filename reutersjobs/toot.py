import csv
import os
import time

import click
from mastodon import Mastodon
from rich import print

from . import utils


@click.command()
def cli():
    """Post latest requests to Mastodon."""
    data = list(csv.DictReader(open(utils.DATA_DIR / "clean" / "additions.csv")))
    print(f"Tooting {len(data)} listings")
    api = Mastodon(
        client_id=os.getenv("MASTODON_CLIENT_KEY"),
        client_secret=os.getenv("MASTODON_CLIENT_SECRET"),
        access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
        api_base_url="https://mastodon.palewi.re",
    )
    for obj in data:
        image_path = utils.DATA_DIR / "img" / f"{obj['id']}.png"
        assert image_path.exists()
        title = utils.clean_title(obj["title"])
        media_obj = api.media_post(image_path, description=title)
        text = f"""🟠 {title} in {obj['city']} {obj['url']}"""
        api.status_post(text, media_ids=media_obj["id"])
        time.sleep(2)


if __name__ == "__main__":
    cli()
