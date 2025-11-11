from __future__ import annotations

from datetime import datetime

from nfl_injury_report.main import (
    format_report_text,
    generate_output_filename,
    parse_args,
)
from nfl_injury_report.scraper import DataTable, ScrapedReport


def test_generate_output_filename_uses_expected_pattern() -> None:
    timestamp = datetime(2024, 1, 2, 15, 4, 5)
    assert (
        generate_output_filename(now=timestamp)
        == "InjuryNews_2024-01-02__Tuesday_15-04-05.txt"
    )


def test_format_report_text_includes_summary_and_table_data() -> None:
    summary = "Team summary"
    reports = [
        ScrapedReport(
            team_name="Example Team",
            url="http://example.com",
            tables=[
                DataTable(
                    headers=["Player", "Status"],
                    rows=[["John Doe", "Out"], ["Jane Doe", "Questionable"]],
                )
            ],
        )
    ]

    content = format_report_text(summary, reports)

    assert "Summary" in content
    assert "Team: Example Team" in content
    assert "Player | Status" in content
    assert "John Doe | Out" in content
    assert "Jane Doe | Questionable" in content


def test_parse_args_supports_no_email_flag() -> None:
    args = parse_args(["--no-email"])
    assert not args.send_email
    assert not args.debug


def test_parse_args_supports_debug_flag() -> None:
    args = parse_args(["--debug"])
    assert args.debug
