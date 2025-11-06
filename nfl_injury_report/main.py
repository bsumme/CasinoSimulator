"""Command line entry point for scraping and emailing NFL injury reports."""

from __future__ import annotations

import argparse
import sys

from .emailer import InjuryReportEmailer
from .scraper import ChromeFetcher, InjuryReportScraper
from .summarizer import summarise_reports
from .teams import NFL_TEAMS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Skip sending an email and just print the summary to stdout",
    )
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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    fetcher = ChromeFetcher(binary=args.chrome_binary)
    scraper = InjuryReportScraper(fetcher=fetcher)

    try:
        teams = NFL_TEAMS
        if args.limit is not None:
            teams = teams[: args.limit]

        reports = scraper.scrape_many(teams)
        summary = summarise_reports(reports)
        print(summary)

        if not args.no_email:
            emailer = InjuryReportEmailer.from_environment()
            message = emailer.build_email(reports)
            emailer.send_email(message)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
