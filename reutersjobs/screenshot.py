import os
import csv
import time

import click
from rich import print

from . import utils


@click.command()
def cli():
    """Post latest requests to Twitter."""
    data = list(csv.DictReader(open(utils.DATA_DIR / "clean" / "additions.csv", "r")))
    print(f"Screenshoting {len(data)} listings")
    for obj in data:
        os.system(f"shot-scraper http://localhost:8000/job/?id={obj['id']} -s '.module-border-wrap' -o {utils.DATA_DIR / 'img'}/{obj['id']}.png -w 1200 -h 630")
        time.sleep(2)


if __name__ == "__main__":
    cli()
