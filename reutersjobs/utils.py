import re
import csv
import json
import typing
from pathlib import Path

from dateutil.parser import parse as dateparse
from rich import print

THIS_DIR = Path(__file__).parent.absolute()
DATA_DIR = THIS_DIR.parent / "data"


def clean_title(t: str) -> str:
    """Tidy up the title."""
    t = t.replace("- Reuters", "")
    t = t.replace("– Reuters", "")
    t = t.replace(", Reuters", "")
    t = t.replace("Latam ", "Latin American ")
    t = re.sub(r"\([^)]*\)", "", t)
    return t.strip()


def write_csv(
    data: typing.Any, path: Path, fieldnames: typing.Optional[typing.List] = None
):
    """Write JSON data to the provided path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 Writing CSV to {path}")
    with open(path, "w") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames or data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def write_json(data: typing.Any, path: Path, indent: int = 2):
    """Write JSON data to the provided path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 Writing JSON to {path}")
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def get_latest_list() -> typing.List[typing.Dict]:
    """Open the latest jobs list."""
    with open(DATA_DIR / "clean" / "latest.csv") as fp:
        reader = csv.DictReader(fp)
        row_list = list(reader)
    return row_list


def get_sorted_file_list(
    data_dir: Path = DATA_DIR / "clean", ext: str = ".csv"
) -> typing.List[Path]:
    """Return the CSV files from our clean data directory in reverse chronological order."""
    # Get all the JSON files
    file_list = list(data_dir.glob(f"*{ext}"))

    # Parse them
    file_tuples = []
    for f in file_list:
        if f.stem == "additions":
            continue
        elif f.stem == "latest":
            continue
        file_tuples.append((dateparse(f.stem), f))

    # Sort them
    sorted_list = sorted(file_tuples, key=lambda x: x[0], reverse=True)

    # Return the path objects
    return [t[1] for t in sorted_list]
