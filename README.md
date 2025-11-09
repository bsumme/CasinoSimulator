# NFL Injury Report Tracker

This repository hosts a Python utility for collecting and distributing weekly NFL injury updates. The tool
uses a headless Chrome session to gather publicly available injury reports for every team, summarises notable
changes, and optionally emails a consolidated digest to interested recipients.

## Project structure

```
.
└── nfl_injury_report   # Python package containing the scraper, summariser, and emailer modules
```

## Getting started

Create and activate a Python 3.11+ virtual environment, then install the dependencies listed in
`nfl_injury_report/requirements.txt` if present or install your own browser automation stack.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r nfl_injury_report/requirements.txt  # optional helper if you maintain a requirements file
```

Set the environment variables used by the email sender before running the tool:

- `SMTP_HOST`
- `SMTP_PORT` (defaults to `587`)
- `SMTP_USER` and `SMTP_PASSWORD`
- `SMTP_SENDER` (defaults to `SMTP_USER`)
- `INJURY_REPORT_RECIPIENT` (comma-separated list)

Launch the scraper with:

```bash
python -m nfl_injury_report.main
```

### Useful flags

- `--no-email` – Skip the email stage and only print the summarised report.
- `--chrome-binary` – Provide an explicit Chrome or Chromium executable path.
- `--limit N` – Restrict scraping to the first `N` teams (helpful for debugging).

## Tests

The project includes a small pytest suite:

```bash
pip install pytest
pytest nfl_injury_report/tests
```

## License

This project removes all prior casino simulation assets and now focuses solely on the open-source NFL injury
report tracking workflow.
