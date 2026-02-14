#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
# ]
# ///
#
# 
# TODO:
# How to use a CORS proxy to get around "No Access-Control-Allow-Origin header" 
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS

# Show next trains arriving at a SEPTA Regional Rail station

import argparse
import logging
import urllib.parse
from datetime import datetime

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def fetch_response(station: str, direction: str) -> dict:
    """
    Fetch raw JSON response from SEPTA Arrivals API.

    Parameters
    ----------
    station: Station name (e.g. 'Suburban Station')
    direction: 'N' for Northbound or 'S' for Southbound

    Returns
    -------
    dict: Raw JSON response from the API

    """

    #URLs cannot contain literal spaces
    encoded_station = urllib.parse.quote(station)

    API_URL = "https://www3.septa.org/api/Arrivals/index.php"
    url = f"{API_URL}?station={encoded_station}&direction={direction}"
    logging.info(f"Fetching {direction}bound arrivals from {url}")

    #TODO requests error handling
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    return data
    

def process_response(data: dict) -> list[dict]:
    """
    Extract train arrivals list from SEPTA API response.

    Parameters
    ----------
    data: Raw JSON response from SEPTA API

    Returns
    -------
    list[dict]: List of train arrival dicts, or empty list if none

    """
    
    # SEPTA API response is a dict with one key value pair containing 
    # a list containing a dict with one key value pair

    station, trains = data.popitem()
    if not trains:
        return []
    direction, train_arrivals = trains[0].popitem()

    return train_arrivals
    


def fetch_arrivals(station: str, direction: str) -> list[dict]:
    """
    Fetch train arrivals for a station and direction (N or S).

    Parameters
    ----------
    station: Station name (e.g. 'Suburban Station')
    direction: 'N' for Northbound or 'S' for Southbound

    Returns
    -------
    list[dict]: List of train arrival dicts, or empty list if none

    """
    data = fetch_response(station, direction)

    return process_response(data)


def minutes_until(depart_time_str: str) -> int | None:
    """
    Calculate minutes until a departure time.
    
    Parameters:
    ----------
    depart_time_str: 
    
    
    Returns:
    -------
    
    """
    try:
        depart = datetime.strptime(depart_time_str, "%Y-%m-%d %H:%M:%S.%f")
        now = datetime.now()
        delta = depart - now
        return max(0, int(delta.total_seconds() / 60))
    except (ValueError, TypeError):
        return None


def format_train(train: dict) -> str:
    """
    Format a single train arrival for display.
    
    Parameters
    ----------
    train: 
        
    Returns
    -------
    
    """
    line = train.get("line", "?")
    destination = train.get("destination", "?")
    track = train.get("track", "?")
    depart_time = train.get("depart_time", "")
    sched_time = train.get("sched_time", "")

    mins = minutes_until(depart_time)
    countdown = f"{mins} min" if mins is not None and mins > 0 else "now" if mins == 0 else "?"

    sched_short = ""
    try:
        dt = datetime.strptime(sched_time, "%Y-%m-%d %H:%M:%S.%f")
        sched_short = dt.strftime("%-I:%M %p")
    except (ValueError, TypeError):
        pass

    # TODO: Split off train arrival data from formatting 

    return f"  {sched_short:<10} {line:<18} to {destination:<22} Trk {track:<3} [{countdown}]"


def display_direction(trains: list[dict], label: str, count: int = 4) -> None:
    """
    Display trains for one direction.
    
    Parameters
    ----------
    trains:
    label:
    count:
    
    
    Returns
    -------
    
    
    """
    print(f"\n{'─' * 70}")
    print(f"  {label}")
    print(f"{'─' * 70}")
    if not trains:
        print("  No trains scheduled")
        return
    print(f"  {'Sched':<10} {'Line':<18}    {'Destination':<22} {'Trk':<6} {'Arrives'}")
    print(f"  {'─'*10} {'─'*18}    {'─'*22} {'─'*6} {'─'*10}")
    for train in trains[:count]:
        print(format_train(train))


def main():
    parser = argparse.ArgumentParser(description="SEPTA Regional Rail next arrivals")
    parser.add_argument("station", type=str, help="Station name (e.g. 'Suburban Station')")
    # TODO: Add an argument for the number of next arrivals
    args = parser.parse_args()

    station = args.station
    
    #TODO: Sanitize Regional Rail Inputs https://www3.septa.org/VIRegionalRail.html
    
    print(f"\n  Station: {station}")
    print(f"  As of:   {datetime.now().strftime('%B %d, %Y %-I:%M %p')}")

    northbound = fetch_arrivals(station, "N")
    southbound = fetch_arrivals(station, "S")

    display_direction(northbound, "NORTHBOUND", count=4)
    display_direction(southbound, "SOUTHBOUND", count=4)
    print()


if __name__ == "__main__":
    main()
