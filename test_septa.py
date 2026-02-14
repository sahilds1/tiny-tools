import pytest

from septa import process_response

def test_process_response_extracts_trains():
    data = {
        "Suburban Station Departures: January 28, 2026, 7:27 pm": [
            {
                "Northbound": [
                    {"destination": "Fox Chase", "line": "Fox Chase"},
                    {"destination": "Temple U", "line": "Warminster"},
                ]
            }
        ]
    }

    trains = process_response(data)

    assert len(trains) == 2
    assert trains[0]["destination"] == "Fox Chase"
    assert trains[0]["line"] == "Fox Chase"
    assert trains[1]["destination"] == "Temple U"
    assert trains[1]["line"] == "Warminster"


def test_process_response_empty_trains_list():
    data = {"Suburban Station Departures: ...": []}

    trains = process_response(data)

    assert trains == []


def test_process_response_empty_dict():
    data = {}

    with pytest.raises(KeyError):
        process_response(data)