import json
from datetime import datetime
from pathlib import Path

import click
import pytz

from . import utils

# from markdownify import markdownify


@click.command()
def cli():
    """Tranform and clean raw data."""
    # Set directories
    THIS_DIR = Path(__file__).parent.absolute()
    DATA_DIR = THIS_DIR.parent / "data"

    # Read in the latest raw data
    latest_raw_path = DATA_DIR / "raw" / "latest.json"
    latest_data = json.load(open(latest_raw_path))

    # Trim down the data
    clean_job_list = []
    for raw_job in latest_data:
        clean_job = dict(
            id=raw_job["jobId"],
            title=raw_job["title"],
            url=raw_job["applyUrl"],
            open_date=raw_job["postedDate"],
            type=raw_job["type"],
            city=raw_job["city"],
            country=raw_job["country"],
            x=raw_job["longitude"],
            y=raw_job["latitude"],
        )
        clean_job_list.append(clean_job)

    print(f"✨ Cleaned {len(clean_job_list)} jobs")

    # Get the current time
    tz = pytz.timezone("Europe/London")
    now = datetime.now(tz=tz)

    # Write them out
    utils.write_csv(clean_job_list, DATA_DIR / "clean" / f"{now}.csv")
    utils.write_csv(clean_job_list, DATA_DIR / "clean" / "latest.csv")

    # Trim the file list so it doesn't get super long
    can_go = utils.get_sorted_file_list()[10:]
    print(f"🗑️ Deleting {len(can_go)} old scrapes")
    for p in can_go:
        p.unlink()


if __name__ == "__main__":
    cli()
