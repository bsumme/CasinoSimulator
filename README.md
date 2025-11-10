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

### Environment configuration

The emailer reads its SMTP configuration from environment variables. The simplest way to manage
them is with a `.env` file in the project root:

```dotenv
# .env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=changeme
SMTP_SENDER="NFL Injury Bot <noreply@example.com>"
INJURY_REPORT_RECIPIENT="alice@example.com,bob@example.com"
```

Load the variables and run the scraper in one command on Linux/macOS shells:

```bash
set -a                     # export everything sourced from the file
source .env
set +a
python -m nfl_injury_report.main --limit 4 --no-email
```

On Windows PowerShell, use:

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^(?<key>[^#=]+)=(?<value>.*)$') {
    Set-Item -Path env:$($Matches.key.Trim()) -Value $Matches.value.Trim('"')
  }
}
python -m nfl_injury_report.main --no-email
```

If you prefer manual exports, set the variables yourself before running `python -m
nfl_injury_report.main`:

- `export SMTP_HOST=...`
- `export SMTP_PORT=587`
- `export SMTP_USER=...`
- `export SMTP_PASSWORD=...`
- `export SMTP_SENDER=...`
- `export INJURY_REPORT_RECIPIENT="alice@example.com,bob@example.com"`

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
