import os
import csv
from operator import itemgetter
from dateutil.parser import parse as dateparse

import click
from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator
from rich import print

from . import utils


@click.command()
def cli():
    """Post latest requests to Twitter."""
    # Get latest data
    data = list(csv.DictReader(open(utils.DATA_DIR / "clean" / "latest.csv")))

    # Parse dates
    rss_data = []
    for r in data:
        r["open_date"] = dateparse(r["open_date"])
        rss_data.append(r)

    # Sort reverse chron
    sorted_data = sorted(rss_data, key=itemgetter("open_date"), reverse=True)

    print("Creating RSS")

    # Slice the most recent 50 for inclusion in our feed
    feed_data = sorted_data[:50]

    # Create our feed object
    fg = FeedGenerator()
    fg.title("Lastest Reuters job listings")
    fg.link(href="https://jobs.thomsonreuters.com/")
    fg.description(
        "All the latest journalist jobs at Reuters, the world's biggest independent newsroom"
    )

    # Add our feed entries
    for row in feed_data:
        entry = FeedEntry()
        entry.id(r["id"])
        title = utils.clean_title(row["title"])
        entry.title(f"{title} in {row['city']}")
        entry.published(row["open_date"])
        entry.link(href=row["url"])
        entry.enclosure(
            url=f"https://raw.githubusercontent.com/palewire/reuters-jobs/main/data/img/{row['id']}.png",
            type="image/png",
            length=os.path.getsize(utils.DATA_DIR / "img" / f"{row['id']}.png"),
        )
        fg.add_entry(entry, order="append")

    # Write it out
    fg.rss_file(utils.DATA_DIR / "clean" / "latest.rss", pretty=True)


if __name__ == "__main__":
    cli()
