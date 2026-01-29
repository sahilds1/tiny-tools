#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
# ]
# ///

# Show next trains arriving at a SEPTA Regional Rail station

import argparse
import logging
import urllib.parse
from datetime import datetime

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

API_URL = "https://www3.septa.org/api/Arrivals/index.php"


def fetch_arrivals(station: str, direction: str) -> list[dict]:
    """Fetch train arrivals for a station and direction (N or S)."""
    encoded = urllib.parse.quote(station)
    url = f"{API_URL}?station={encoded}&direction={direction}"
    logging.info(f"Fetching {direction}bound arrivals from {url}")

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # Response is a dict with one key (station + timestamp), containing a list
    # with one dict that has "Northbound" or "Southbound" key
    for key, trains_list in data.items():
        if trains_list:
            entry = trains_list[0]
            direction_key = "Northbound" if direction == "N" else "Southbound"
            return entry.get(direction_key, [])
    return []


def minutes_until(depart_time_str: str) -> int | None:
    """Calculate minutes until a departure time."""
    try:
        depart = datetime.strptime(depart_time_str, "%Y-%m-%d %H:%M:%S.%f")
        now = datetime.now()
        delta = depart - now
        return max(0, int(delta.total_seconds() / 60))
    except (ValueError, TypeError):
        return None


def format_train(train: dict) -> str:
    """Format a single train arrival for display."""
    line = train.get("line", "?")
    destination = train.get("destination", "?")
    status = train.get("status", "?")
    track = train.get("track", "?")
    depart_time = train.get("depart_time", "")
    sched_time = train.get("sched_time", "")

    mins = minutes_until(depart_time)
    if mins is not None:
        countdown = f"{mins} min" if mins > 0 else "now"
    else:
        countdown = status

    sched_short = ""
    try:
        dt = datetime.strptime(sched_time, "%Y-%m-%d %H:%M:%S.%f")
        sched_short = dt.strftime("%-I:%M %p")
    except (ValueError, TypeError):
        pass

    return f"  {sched_short:<10} {line:<18} to {destination:<22} Trk {track:<3} [{countdown}] ({status})"


def display_direction(trains: list[dict], label: str, count: int = 4) -> None:
    """Display trains for one direction."""
    print(f"\n{'─' * 70}")
    print(f"  {label}")
    print(f"{'─' * 70}")
    if not trains:
        print("  No trains scheduled")
        return
    print(f"  {'Sched':<10} {'Line':<18}    {'Destination':<22} {'Trk':<6} {'Arrives'}")
    print(f"  {'─'*10} {'─'*18}    {'─'*22} {'─'*6} {'─'*20}")
    for train in trains[:count]:
        print(format_train(train))


def main():
    parser = argparse.ArgumentParser(description="SEPTA Regional Rail next arrivals")
    parser.add_argument("station", type=str, help="Station name (e.g. 'Suburban Station')")
    args = parser.parse_args()

    station = args.station
    print(f"\n  Station: {station}")
    print(f"  As of:   {datetime.now().strftime('%B %d, %Y %-I:%M %p')}")

    northbound = fetch_arrivals(station, "N")
    southbound = fetch_arrivals(station, "S")

    display_direction(northbound, "NORTHBOUND", count=4)
    display_direction(southbound, "SOUTHBOUND", count=4)
    print()


if __name__ == "__main__":
    main()
