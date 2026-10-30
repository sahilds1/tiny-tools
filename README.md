# Tiny Tools

Small personal utilities

## websters1913: Word definitions from Webster's 1913 dictionary

A command line tool to [output word definitions from websters1913.com](https://jsomers.net/blog/dictionary)

Execute [using `uv` to manage dependencies](https://docs.astral.sh/uv/guides/scripts/) without manually managing environments:

```sh
uv run websters1913.py --word pathos
```

Execute without using uv run by adding the script to your PATH and ensuring it is executable:

```sh
websters1913.py --word pathos
```

## leetcode_launcher: LeetCode Problem Opener

A command-line tool to open a LeetCode problem in your browser by specifying its problem number

Execute [using `uv` to manage dependencies](https://docs.astral.sh/uv/guides/scripts/) without manually managing environments:

```sh
uv run leetcode_launcher.py --num 1
```

Execute without using uv run by adding the script to your PATH and ensuring it is executable:

```sh
leetcode_launcher.py --num 1
```

## llm_commit_message: Generate a commit message based on a diff input

A command line tool to generate a commit message based on a diff input

Execute [using `uv` to manage dependencies](https://docs.astral.sh/uv/guides/scripts/) without manually managing environments:

```sh
git diff --cached | uv run --script llm_commit_message.py | cat
```

Execute without using uv run by adding the script to your PATH and ensuring it is executable:

```sh
git diff --cached | llm_commit_message.py | cat
```

## septa: SEPTA Regional Rail arrivals

A command line tool to show the next train arrivals at a SEPTA Regional Rail station

Execute [using `uv` to manage dependencies](https://docs.astral.sh/uv/guides/scripts/) without manually managing environments:

```sh
uv run septa.py "Suburban Station"
```

Execute without using uv run by adding the script to your PATH and ensuring it is executable:

```sh
septa.py "Suburban Station"
```

## strava: Chat with an LLM coach about your Strava activities

A command line tool to fetch Strava activities (by ID, single day, or date range) and analyze them in an interactive chat. The chat is a small agent that can search your running log (`RUNLOG.txt`) for past context

Copy `.env.example` to `.env` and fill in your [Strava API app](https://www.strava.com/settings/api) credentials and `OPENAI_API_KEY`. The first run prints an authorization URL; open it, approve, and paste the redirect URL back. Tokens are saved to `~/.strava_tokens.json` and refreshed automatically

Execute [using `uv` to manage dependencies](https://docs.astral.sh/uv/guides/scripts/) without manually managing environments:

```sh
uv run strava.py --start 2026-07-13 --end 2026-07-19
```

Other ways to select activities, pick a model, or point at a different running log:

```sh
uv run strava.py --id 1234567890
uv run strava.py --date 2026-07-14 -m gpt-5-nano
uv run strava.py --date 2026-07-14 --runlog ~/notes/runlog.md
```

Execute without using uv run by adding the script to your PATH and ensuring it is executable:

```sh
strava.py --start 2026-07-13 --end 2026-07-19
```

## Contributing

Contributions are welcome!

## License
Tiny Tools is licensed under the [Functional Source License, Version 1.1, ALv2 Future License](https://fair.io/licenses/)
