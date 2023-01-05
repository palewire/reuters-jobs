"""Download job listings from the Reuters site."""
import json
import typing
from datetime import datetime
from pathlib import Path

import click
import pytz
import requests
from rich import print


@click.command()
def cli():
    """Download job listings from the Reuters site."""
    # Set the download directory
    this_dir = Path(__file__).parent.absolute()
    data_dir = this_dir.parent / "data" / "raw"

    # Create it, if it doesn't already exist
    data_dir.mkdir(exist_ok=True, parents=True)

    # Pull the raw list
    url = "https://jobsapi-internal.m-cloud.io/api/job?sortfield=open_date&sortorder=descending&Limit=999&Organization=2279&offset=1&fuzzy=false"
    r = requests.get(url)
    assert r.ok
    job_list = r.json()

    # Get the current time
    tz = pytz.timezone("Europe/London")
    now = datetime.now(tz=tz)

    # Write them out
    write_json(job_list, data_dir / f"{now}.json")
    write_json(job_list, data_dir / "latest.json")


def write_json(data: typing.Any, path: Path, indent: int = 2):
    """Write JSON data to the provided path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 Writing JSON to {path}")
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


if __name__ == "__main__":
    cli()
