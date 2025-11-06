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

### Running from the VS Code terminal on Windows/WSL

If you are opening the repository in VS Code on Windows and using the
integrated terminal (either PowerShell or the WSL Ubuntu shell), make sure
that Python 3.11 or newer is available before running the module. The
application uses features that are not present in Python 3.10.

1. **Check your current Python version**

   ```bash
   python3 --version
   ```

   If the output shows `Python 3.11.x` (or newer), you can skip the rest of
   this setup and run the scraper command from the repository root.

2. **Install Python 3.11 inside WSL (Ubuntu)**

   ```bash
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   sudo apt install python3.11 python3.11-venv
   ```

   > If you are running PowerShell without WSL, install Python 3.11 from
   > https://www.python.org/downloads/windows/ and restart VS Code so it picks
   > up the new interpreter.

3. **Create and activate a virtual environment** (recommended)

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

   In PowerShell, replace the `source` command with:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. **Install project dependencies (if any) and run the scraper**

   ```bash
   python3.11 -m pip install -r requirements.txt  # only if you add packages
   python3.11 -m nfl_injury_report.main
   ```

This workflow matches the VS Code “Python: Select Interpreter” command, so you
can also pick the `.venv` interpreter from the Command Palette and use the Run
button in the editor.

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
