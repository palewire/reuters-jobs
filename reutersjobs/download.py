"""Download job listings from the Reuters site."""
from datetime import datetime
from pathlib import Path

import click
import pytz
import requests
from rich import print

from . import utils


@click.command()
def cli():
    """Download job listings from the Reuters site."""
    # Set the download directory
    this_dir = Path(__file__).parent.absolute()
    data_dir = this_dir.parent / "data" / "raw"

    # Create it, if it doesn't already exist
    data_dir.mkdir(exist_ok=True, parents=True)

    # Request the data
    headers = {
        "content-type": "application/json",
    }
    data = {
        "lang": "en_us",
        "deviceType": "desktop",
        "country": "us",
        "pageName": "search-results",
        "ddoKey": "refineSearch",
        "sortBy": "Most recent",
        "subsearch": "",
        "from": 0,
        "jobs": True,
        "counts": True,
        "all_fields": [
            "category",
            "country",
            "state",
            "city",
            "type",
            "remote",
        ],
        "size": 100,
        "clearAll": False,
        "jdsource": "facets",
        "isSliderEnable": False,
        "pageId": "page21",
        "siteType": "external",
        "keywords": "",
        "global": True,
        "selected_fields": {"category": ["News & Editorial Careers"]},
        "sort": {"order": "desc", "field": "postedDate"},
        "locationData": {},
    }

    # Make the request
    resp = requests.post(
        "https://careers.thomsonreuters.com/widgets",
        headers=headers,
        json=data,
    )

    # Get the JSON
    job_list = resp.json()["refineSearch"]["data"]["jobs"]
    print(f"📥 Downloaded {len(job_list)} jobs")

    # Get the current time
    tz = pytz.timezone("Europe/London")
    now = datetime.now(tz=tz)

    # Write them out
    utils.write_json(job_list, data_dir / f"{now}.json")
    utils.write_json(job_list, data_dir / "latest.json")

    # Trim the file list so it doesn't get super long
    can_go = utils.get_sorted_file_list(data_dir=data_dir, ext=".json")[10:]
    print(f"🗑️ Deleting {len(can_go)} old scrapes")
    for p in can_go:
        p.unlink()


if __name__ == "__main__":
    cli()
