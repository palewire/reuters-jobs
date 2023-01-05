import csv
import json
import typing
from datetime import datetime
from pathlib import Path

import click
import pytz
from rich import print

from . import utils


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
    raw_job_list = latest_data["queryResult"]
    clean_job_list = []
    for raw_job in raw_job_list:
        clean_job = dict(
            id=raw_job["id"],
            ref=raw_job["ref"],
            title=raw_job["title"],
            url=raw_job["employment_type"],
            description=utils.strip_html(raw_job["description"]),
            open_date=raw_job["open_date"],
            type=raw_job["employment_type"],
            category=raw_job["primary_category"],
            department=raw_job["department"],
            business_unit=raw_job["business_unit"],
            industry=raw_job["industry"],
            function=raw_job["function"],
            city=raw_job["primary_city"],
            country=raw_job["primary_country"],
            x=raw_job["primary_location"][0],
            y=raw_job["primary_location"][1],
        )
        clean_job_list.append(clean_job)

    # Get the current time
    tz = pytz.timezone("Europe/London")
    now = datetime.now(tz=tz)

    # Write them out
    write_csv(clean_job_list, DATA_DIR / "clean" / f"{now}.csv")
    write_csv(clean_job_list, DATA_DIR / "clean" / "latest.csv")


def write_csv(data: typing.Any, path: Path):
    """Write JSON data to the provided path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 Writing CSV to {path}")
    with open(path, "w") as fh:
        writer = csv.DictWriter(fh, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    cli()
