import csv
import os
import time

import click
import twitter
from rich import print

from . import utils


@click.command()
def cli():
    """Post latest listings to Twitter."""
    data = list(csv.DictReader(open(utils.DATA_DIR / "clean" / "additions.csv")))
    print(f"Tooting {len(data)} listings")
    api = twitter.Api(
        consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
        consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
        access_token_key=os.getenv("TWITTER_ACCESS_TOKEN_KEY"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    )
    for obj in data:
        image_path = utils.DATA_DIR / "img" / f"{obj['id']}.png"
        assert image_path.exists()
        media_obj = api.UploadMediaSimple(open(image_path, "rb"))
        title = utils.clean_title(obj["title"])
        api.PostMediaMetadata(media_obj, title)
        text = f"""🟠 {title} in {obj['city']} {obj['url']}"""
        api.PostUpdate(text, media=media_obj)
        time.sleep(5)


if __name__ == "__main__":
    cli()
