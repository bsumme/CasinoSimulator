# NFL Injury Report Tracker

This repository hosts a Python utility for collecting weekly NFL injury updates. The tool uses a headless
Chrome session to gather publicly available injury reports for every team, summarises notable changes, and
saves the output to a timestamped text file for later review.

## Project structure

```
.
└── nfl_injury_report   # Python package containing the scraper and summariser modules
```

## Getting started

### Prerequisites

- Python **3.11 or newer**
- Google Chrome or Chromium installed locally (the scraper shells out to the browser's headless
  CLI and defaults to `google-chrome`; override with `CHROME_BINARY` or the `--chrome-binary`
  flag if needed)
- `pip` for installing any optional development dependencies such as `pytest`

Create and activate an isolated environment to keep optional tooling separate from your global
Python installation:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

> **Note:** The runtime itself relies solely on the Python standard library, so there are no
> required `pip` packages beyond what ships with CPython. Install additional dependencies only if
> you plan to run tests or linters.

### Useful flags

- `--chrome-binary` – Provide an explicit Chrome or Chromium executable path.
- `--limit N` – Restrict scraping to the first `N` teams (helpful for debugging).
- `--no-email` – Skip any optional email delivery step (useful when running locally).

Running the scraper writes the summary and detailed tables to a file named
`InjuryNews_{Date__DayofWeek_Time}.txt` in the current working directory (for example,
`InjuryNews_2024-01-02__Tuesday_15-04-05.txt`).

## Tests

The project includes a small pytest suite:

```bash
pip install pytest
pytest nfl_injury_report/tests
```

## License

This project removes all prior casino simulation assets and now focuses solely on the open-source NFL injury
report tracking workflow.
