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

from sklearn.feature_extraction.text import TfidfVectorizer

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


def search_entries(
    entries: list[RunlogEntry], query: str, limit: int = 3
) -> list[RunlogEntry]:
    """Rank entries by TF-IDF cosine similarity to the query and return the top `limit`.

    TF-IDF weights each term by how rare it is across the log, so a match on a distinctive
    word (e.g. 'fartlek') outranks a match on a ubiquitous one (e.g. 'run') -- the thing
    plain term-counting got wrong. Entries sharing no terms with the query are dropped;
    ties keep the log's original (chronological) order.
    """
    # Decision: scikit-learn's TfidfVectorizer instead of a hand-rolled scorer. It gives the
    # simplest correct code -- it tokenizes, lowercases, and L2-normalizes for us -- at the
    # cost of a heavy numpy/scipy dependency, declared in BOTH strava.py's script block and
    # pyproject.toml because standalone `uv run strava.py` and `uv run pytest` are different
    # environments. We chose the smaller function over the lighter dependency on purpose.
    #
    # Decision: title text is folded into the document but NOT up-weighted. Runlog titles are
    # just a date + run type, so a title-only boost wasn't worth the extra code; if titles
    # ever need to rank higher, double them here (f"{e.title} {e.title}\n{e.body}").
    #
    # BM25 is the natural next step if ranking needs to improve: it keeps this TF-IDF backbone
    # but adds term-frequency saturation (repeated terms give diminishing returns) and
    # document-length normalization (long entries don't win just by being long). To switch,
    # replace only the vectorize-and-score lines below -- keeping the guard, the `> 0` filter,
    # and the sort/limit tail -- with either rank-bm25
    # (BM25Okapi(tokenized_docs).get_scores(query.split())) or, for a zero-dependency route
    # more in keeping with this repo, SQLite FTS5's built-in bm25().
    if not entries:
        # TfidfVectorizer().fit_transform([]) raises "empty vocabulary"; guard it.
        return []
    docs = [f"{e.title}\n{e.body}" for e in entries]
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(docs)
    # TF-IDF rows are L2-normalized, so this dot product is exactly the cosine similarity.
    # An empty or all-unknown query yields a zero vector, hence all-zero scores -> no matches.
    scores = (vectorizer.transform([query]) @ matrix.T).toarray().ravel()
    # (-scores).argsort is descending; kind="stable" makes earlier entries win ties.
    order = (-scores).argsort(kind="stable")
    # The `> 0` filter is load-bearing: it makes a no-match query return [] (and thus
    # format_entries' "no matching entries" sentinel) rather than unrelated entries.
    return [entries[i] for i in order if scores[i] > 0][:limit]


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
