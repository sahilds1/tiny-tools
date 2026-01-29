from unittest.mock import patch, Mock

from septa import fetch_arrivals

SAMPLE_RESPONSE = {
    "Suburban Station Departures: January 28, 2026, 7:27 pm": [
        {
            "Northbound": [
                {
                    "direction": "N",
                    "path": "R8N",
                    "train_id": "854",
                    "origin": "Gray 30th Street",
                    "destination": "Fox Chase",
                    "line": "Fox Chase",
                    "status": "1 min",
                    "service_type": "LOCAL",
                    "next_station": "30th St",
                    "sched_time": "2026-01-28 19:34:00.000",
                    "depart_time": "2026-01-28 19:35:00.000",
                    "track": "1",
                    "track_change": None,
                    "platform": "B",
                    "platform_change": None,
                },
                {
                    "direction": "N",
                    "path": "R4N",
                    "train_id": "9458",
                    "origin": "Penn Medical Station",
                    "destination": "Temple U",
                    "line": "Warminster",
                    "status": "6 min",
                    "service_type": "LOCAL",
                    "next_station": "Penn Medical Station",
                    "sched_time": "2026-01-28 19:34:00.000",
                    "depart_time": "2026-01-28 19:35:00.000",
                    "track": "2",
                    "track_change": None,
                    "platform": "A",
                    "platform_change": None,
                },
            ]
        }
    ],
}


@patch("septa.requests.get")
def test_fetch_arrivals_northbound(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = SAMPLE_RESPONSE
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    trains = fetch_arrivals("Suburban Station", "N")

    assert len(trains) == 2
    assert trains[0]["destination"] == "Fox Chase"
    assert trains[1]["line"] == "Warminster"
    mock_get.assert_called_once()


@patch("septa.requests.get")
def test_fetch_arrivals_empty_response(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = {"Suburban Station Departures: ...": []}
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    trains = fetch_arrivals("Suburban Station", "N")

    assert trains == []


@patch("septa.requests.get")
def test_fetch_arrivals_southbound_missing(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = SAMPLE_RESPONSE
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    trains = fetch_arrivals("Suburban Station", "S")

    assert trains == []
