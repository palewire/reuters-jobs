import os
import csv
import time

import click
from mastodon import Mastodon
from rich import print

from . import utils


@click.command()
def cli():
    """Post latest requests to Twitter."""
    data = list(csv.DictReader(open(utils.DATA_DIR / "clean" / "additions.csv", "r")))
    print(f"Tooting {len(data)} listings")
    api = Mastodon(
        client_id=os.getenv("MASTODON_CLIENT_KEY"),
        client_secret=os.getenv("MASTODON_CLIENT_SECRET"),
        access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
        api_base_url="https://mastodon.palewi.re",
    )
    for obj in data:
        text = f"""{utils.clean_title(obj['title'])} in {obj['city']}\n\n {obj['url']}"""
        api.status_post(text)
        time.sleep(2)


if __name__ == "__main__":
    cli()
