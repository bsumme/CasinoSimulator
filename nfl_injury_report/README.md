# NFL Injury Report Scraper

This Python utility launches a headless Chrome session, searches Google for the
latest injury report of every NFL team, extracts tabular data that appears on
the linked page, summarises notable updates, and emails the consolidated
report.

## Prerequisites

* Python 3.11+
* Google Chrome (or Chromium) installed locally

## Usage

Set the SMTP-related environment variables:

* `SMTP_HOST`
* `SMTP_PORT` (defaults to `587` if omitted)
* `SMTP_USER` and `SMTP_PASSWORD` (if authentication is required)
* `SMTP_SENDER` (defaults to `SMTP_USER` when not specified)
* `INJURY_REPORT_RECIPIENT` (comma separated list of recipients)

Run the scraper:

```bash
python -m nfl_injury_report.main
```

Useful flags:

* `--no-email` – Skip the email step and only print the summary.
* `--chrome-binary` – Provide a custom Chrome/Chromium executable path.
* `--limit N` – Only scrape the first `N` teams for debugging.

## Tests

The included unit tests require `pytest`:

```bash
pip install pytest
pytest nfl_injury_report/tests
```
