import csv

import click
from rich import print

from . import utils


@click.command()
def cli():
    """Integrate files and identify any additions."""
    # Pluck out the last two scrapes for comparison
    file_list = utils.get_sorted_file_list()
    latest_file = file_list[0]
    previous_file = file_list[1]
    print(f"🕵️ Comparing {latest_file.stem}.csv against {previous_file.stem}.csv")

    latest_data = _open_csv(latest_file)
    previous_data = _open_csv(previous_file)

    # Find the new filing ids that are not in the previous file
    previous_filing_ids = [d["id"] for d in previous_data]
    new_data = []
    for d in latest_data:
        if d["id"] not in previous_filing_ids and d["category"] == "News & Editorial":
            new_data.append(d)
    print(f"🆕 {len(new_data)} new filings found")

    # Write out to a CSV
    new_path = utils.DATA_DIR / "clean" / "additions.csv"
    utils.write_csv(new_data, new_path, fieldnames=latest_data[0].keys())


def _open_csv(path):
    return list(csv.DictReader(open(path)))


if __name__ == "__main__":
    cli()
