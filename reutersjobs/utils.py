import csv
import json
import typing
from pathlib import Path

from rich import print


def write_csv(data: typing.Any, path: Path):
    """Write JSON data to the provided path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 Writing CSV to {path}")
    with open(path, "w") as fh:
        writer = csv.DictWriter(fh, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def write_json(data: typing.Any, path: Path, indent: int = 2):
    """Write JSON data to the provided path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 Writing JSON to {path}")
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
