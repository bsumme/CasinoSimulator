"""Command line entry point for scraping NFL injury reports."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

from .scraper import ChromeFetcher, InjuryReportScraper, ScrapedReport
from .summarizer import summarise_reports
from .teams import NFL_TEAMS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chrome-binary",
        default=None,
        help="Path to the Chrome or Chromium executable (defaults to google-chrome)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only scrape the first N teams (useful for debugging)",
    )
    parser.add_argument(
        "--no-email",
        dest="send_email",
        action="store_false",
        help="Skip the optional email delivery step",
    )
    parser.set_defaults(send_email=True)
    return parser.parse_args(argv)


def generate_output_filename(now: datetime | None = None) -> str:
    """Return the timestamped filename for saving injury news."""

    now = now or datetime.now()
    return now.strftime("InjuryNews_%Y-%m-%d__%A_%H-%M-%S.txt")


def format_report_text(summary: str, reports: list[ScrapedReport]) -> str:
    """Create a human-readable representation of the injury reports."""

    lines: list[str] = ["Summary", summary.strip(), ""]

    if not reports:
        lines.append("No detailed reports were generated.")
        return "\n".join(lines) + "\n"

    for report in reports:
        lines.append(f"Team: {report.team_name}")
        if report.url:
            lines.append(f"Source: {report.url}")
        if report.error:
            lines.append(f"Error: {report.error}")
        if report.tables:
            for table in report.tables:
                if table.is_empty():
                    continue
                header_line = " | ".join(table.headers)
                separator_line = "-+-".join("-" * len(header) for header in table.headers)
                lines.append(header_line)
                if separator_line:
                    lines.append(separator_line)
                lines.extend(" | ".join(row) for row in table.rows)
                lines.append("")
        else:
            lines.append("No table data was captured.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    fetcher = ChromeFetcher(binary=args.chrome_binary)
    scraper = InjuryReportScraper(fetcher=fetcher)

    teams = NFL_TEAMS
    if args.limit is not None:
        teams = teams[: args.limit]

    reports = scraper.scrape_many(teams)
    summary = summarise_reports(reports)
    print(summary)

    filename = generate_output_filename()
    file_path = Path.cwd() / filename
    content = format_report_text(summary, reports)
    file_path.write_text(content, encoding="utf-8")
    print(f"Saved detailed report to {file_path}")

    if not args.send_email:
        print("Email delivery skipped (--no-email specified)")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
