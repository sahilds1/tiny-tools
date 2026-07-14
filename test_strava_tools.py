from strava_tools import (
    RunlogEntry,
    format_entries,
    parse_runlog,
    search_entries,
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


# The search_entries tests cover only the wrapping logic we wrote around TfidfVectorizer --
# the empty-corpus guard, the score > 0 filter (which drives the no-match sentinel), and the
# limit slice. They deliberately do NOT assert ranking order: that's scikit-learn's TF-IDF
# behavior, which we don't own and shouldn't re-test.


def test_search_entries_empty_corpus():
    assert search_entries([], "anything") == []


def test_search_entries_no_shared_terms_returns_empty():
    entries = [RunlogEntry("A", "hill repeats"), RunlogEntry("B", "recovery jog")]
    assert search_entries(entries, "cycling swimming") == []


def test_search_entries_respects_limit():
    entries = [RunlogEntry(t, "tempo run") for t in ("A", "B", "C")]
    assert len(search_entries(entries, "tempo", limit=2)) == 2


def test_format_entries_no_match_sentinel():
    assert format_entries([]) == "No matching runlog entries found."
