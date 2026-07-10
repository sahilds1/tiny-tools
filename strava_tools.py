# Tools for the strava.py chat agent, exposed to the LLM via `llm`'s tool-calling
# (model.conversation(tools=[...]) + conversation.chain(...)). `llm` builds each tool's
# schema from the function signature and uses its docstring as the description shown to the
# model, so search_runlog's docstring is written for the model to read.
#
# Structure mirrors the repo's fetch_*/process_*/format_* seam: the pure helpers
# (parse_runlog, search_entries, format_entries) do no I/O and are the test targets;
# search_runlog is the thin tool wrapper that reads the file and glues them together.

from pathlib import Path
from typing import NamedTuple

# Default runlog location (the RUNLOG.txt next to this script). strava.py can override this
# module attribute from its --runlog flag, and tests point it at a fixture file.
RUNLOG_PATH = Path(__file__).parent / "RUNLOG.txt"


class RunlogEntry(NamedTuple):
    title: str
    body: str


def parse_runlog(text: str) -> list[RunlogEntry]:
    """Split raw runlog text into entries.

    An entry starts at a "title" line -- a non-blank line that is not a bullet ("- ...") --
    and runs until the next title line. Blank and bullet lines in between form the body.
    This tolerates the title / blank-line / bullets layout in RUNLOG.txt without needing a
    strict blank-line delimiter between entries.
    """
    entries: list[RunlogEntry] = []
    title: str | None = None
    body_lines: list[str] = []

    def flush() -> None:
        if title is not None:
            entries.append(RunlogEntry(title=title, body="\n".join(body_lines).strip()))

    for raw in text.splitlines():
        line = raw.rstrip()
        is_title = bool(line.strip()) and not line.lstrip().startswith("-")
        if is_title:
            flush()
            title = line.strip()
            body_lines = []
        elif title is not None:
            body_lines.append(line)
    flush()
    return entries


def _tokenize(s: str) -> list[str]:
    """Lowercase alphanumeric word tokens, so 'Half-Marathon!' -> ['half', 'marathon']."""
    return ["".join(c for c in tok if c.isalnum()) for tok in s.lower().split() if tok]


def search_entries(
    entries: list[RunlogEntry], query: str, limit: int = 3
) -> list[RunlogEntry]:
    """Rank entries by case-insensitive query-term matches and return the top `limit`.

    A term found in the title counts double a term found in the body. Entries with no
    matching term are dropped; ties keep the original (chronological) order.
    """
    terms = set(_tokenize(query))
    if not terms:
        return []

    scored: list[tuple[int, int, RunlogEntry]] = []
    for i, entry in enumerate(entries):
        title_tokens = set(_tokenize(entry.title))
        body_tokens = set(_tokenize(entry.body))
        score = 2 * len(terms & title_tokens) + len(terms & body_tokens)
        if score > 0:
            # Negate index so a stable sort keeps earlier entries first within a score tier.
            scored.append((score, -i, entry))

    scored.sort(reverse=True)
    return [entry for _, _, entry in scored[:limit]]


def format_entries(entries: list[RunlogEntry]) -> str:
    """Render matched entries back to plain text for the model (self-contained: the returned
    string is the only thing that survives into the next turn, so include titles + bodies)."""
    if not entries:
        return "No matching runlog entries found."
    return "\n\n".join(f"{e.title}\n{e.body}".rstrip() for e in entries)


def search_runlog(query: str) -> str:
    """Search the athlete's past running log for entries relevant to `query`
    (for example: 'half marathon pacing', 'late-run fade', 'hill workouts').
    Returns the most relevant past run notes and coaching advice as text. Call this
    to compare the current activity against past runs or to recall prior guidance,
    and ground any claims about the athlete's history in what it returns."""
    text = Path(RUNLOG_PATH).read_text()
    return format_entries(search_entries(parse_runlog(text), query))
