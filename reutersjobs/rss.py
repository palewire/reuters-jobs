import csv
from dateutil.parser import parse as dateparse

import click
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
        if r["category"] == "News & Editorial":
            r["open_date"] = dateparse(r["open_date"])
            rss_data.append(r)

    # Sort reverse chron
    sorted_data = sorted(rss_data, key=lambda x: x["open_date"], reverse=True)

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
    for row in reversed(feed_data):
        fe = fg.add_entry()
        fe.id(row["id"])
        title = utils.clean_title(row["title"])
        fe.title(f"{title} in {row['city']}")
        fe.link(href=row["url"])

    # Write it out
    fg.rss_file(utils.DATA_DIR / "clean" / "latest.rss", pretty=True)


if __name__ == "__main__":
    cli()
