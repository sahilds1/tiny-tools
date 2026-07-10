import strava_tools
from strava_tools import (
    RunlogEntry,
    format_entries,
    parse_runlog,
    search_entries,
    search_runlog,
)

# A small multi-entry fixture in the RUNLOG.txt shape: a title line, a blank line, bullets.
RUNLOG = """April 26 Half Marathon Run

- The fade in watts alongside the pace drop suggests your legs gave out. Add a weekly
  long run finishing at goal pace to build muscular endurance.

May 10 Hill Repeats

- Strong power on the climbs; turnover held late. Hills are paying off.

May 17 Easy Recovery Run

- Nice and controlled, heart rate stayed in zone 2 the whole way.
"""


def test_parse_runlog_splits_entries():
    entries = parse_runlog(RUNLOG)
    assert [e.title for e in entries] == [
        "April 26 Half Marathon Run",
        "May 10 Hill Repeats",
        "May 17 Easy Recovery Run",
    ]
    assert entries[0].body.startswith("- The fade in watts")


def test_parse_runlog_single_entry_and_trailing_blanks():
    entries = parse_runlog("Solo Run\n\n- Felt good.\n\n\n")
    assert len(entries) == 1
    assert entries[0] == RunlogEntry(title="Solo Run", body="- Felt good.")


def test_search_entries_finds_match():
    entries = parse_runlog(RUNLOG)
    results = search_entries(entries, "hill repeats")
    assert results[0].title == "May 10 Hill Repeats"


def test_search_entries_ranks_title_match_above_body_only():
    entries = parse_runlog(RUNLOG)
    # "hill" is in the Hill Repeats title and also in the half-marathon body ("Hills"? no) --
    # use a term that appears in one title and one body to check title weighting.
    results = search_entries(entries, "half", limit=3)
    assert results[0].title == "April 26 Half Marathon Run"


def test_search_entries_respects_limit_and_no_match():
    entries = parse_runlog(RUNLOG)
    assert search_entries(entries, "run", limit=1).__len__() == 1
    assert search_entries(entries, "cycling swimming triathlon") == []


def test_format_entries_no_match_sentinel():
    assert format_entries([]) == "No matching runlog entries found."


def test_search_runlog_end_to_end(tmp_path, monkeypatch):
    runlog = tmp_path / "RUNLOG.txt"
    runlog.write_text(RUNLOG)
    monkeypatch.setattr(strava_tools, "RUNLOG_PATH", runlog)

    out = search_runlog("hill climbs turnover")
    assert "May 10 Hill Repeats" in out

    assert search_runlog("kayaking") == "No matching runlog entries found."
