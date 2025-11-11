"""Command line entry point for scraping NFL injury reports."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path
import sys

from .scraper import ChromeFetcher, InjuryReportScraper, ScrapedReport
from .summarizer import summarise_reports
from .teams import NFL_TEAMS

logger = logging.getLogger(__name__)


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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug logging output",
    )
    return parser.parse_args(argv)


def generate_output_filename(now: datetime | None = None) -> str:
    """Return the timestamped filename for saving injury news."""

    now = now or datetime.now()
    filename = now.strftime("InjuryNews_%Y-%m-%d__%A_%H-%M-%S.txt")
    logger.debug("Generated output filename", extra={"filename": filename})
    return filename


def format_report_text(summary: str, reports: list[ScrapedReport]) -> str:
    """Create a human-readable representation of the injury reports."""

    logger.debug(
        "Formatting report text",
        extra={"summary_length": len(summary), "report_count": len(reports)},
    )
    lines: list[str] = ["Summary", summary.strip(), ""]

    if not reports:
        logger.debug("No detailed reports available to format")
        lines.append("No detailed reports were generated.")
        return "\n".join(lines) + "\n"

    for report in reports:
        lines.append(f"Team: {report.team_name}")
        if report.url:
            lines.append(f"Source: {report.url}")
        if report.error:
            lines.append(f"Error: {report.error}")
        if report.tables:
            logger.debug(
                "Formatting tables for team",
                extra={"team": report.team_name, "table_count": len(report.tables)},
            )
            for table in report.tables:
                if table.is_empty():
                    logger.debug(
                        "Skipping empty table during formatting",
                        extra={"team": report.team_name},
                    )
                    continue
                header_line = " | ".join(str(header) for header in table.headers)
                separator_line = "-+-".join("-" * len(str(header)) for header in table.headers)
                lines.append(header_line)
                if separator_line:
                    lines.append(separator_line)
                lines.extend(
                    " | ".join("" if cell is None else str(cell) for cell in row)
                    for row in table.rows
                )
                lines.append("")
        else:
            lines.append("No table data was captured.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    logger.debug("Arguments parsed", extra={"args": vars(args)})

    fetcher = ChromeFetcher(binary=args.chrome_binary)
    scraper = InjuryReportScraper(fetcher=fetcher)

    teams = NFL_TEAMS
    if args.limit is not None:
        logger.debug("Limiting teams", extra={"limit": args.limit})
        teams = teams[: args.limit]

    logger.debug("Starting scrape", extra={"team_count": len(teams)})
    reports = scraper.scrape_many(teams)
    summary = summarise_reports(reports)
    print(summary)

    filename = generate_output_filename()
    file_path = Path.cwd() / filename
    logger.debug("Writing report to file", extra={"path": str(file_path)})
    content = format_report_text(summary, reports)
    file_path.write_text(content, encoding="utf-8")
    print(f"Saved detailed report to {file_path}")

    if not args.send_email:
        print("Email delivery skipped (--no-email specified)")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
