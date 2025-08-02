# Tiny Tools

Small personal utilities

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

## Contributing

Contributions are welcome!

## License
Tiny Tools is licensed under the [Functional Source License, Version 1.1, ALv2 Future License](https://fair.io/licenses/)
