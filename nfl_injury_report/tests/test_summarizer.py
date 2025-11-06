from __future__ import annotations

from nfl_injury_report.scraper import DataTable, ScrapedReport
from nfl_injury_report.summarizer import summarise_report, summarise_reports


def make_table() -> DataTable:
    return DataTable(
        headers=["Player", "Status", "Injury"],
        rows=[
            ["John Doe", "Questionable", "Ankle"],
            ["Jane Smith", "Active", ""],
        ],
    )


def make_report(team: str, table: DataTable | None = None, error: str | None = None) -> ScrapedReport:
    tables = [] if table is None else [table]
    return ScrapedReport(team_name=team, url="http://example.com", tables=tables, error=error)


def test_summarise_report_includes_priority_injuries():
    report = make_report("Test Team", make_table())

    summary = summarise_report(report)
    assert "John Doe (Ankle) - Questionable" in summary
    assert "Jane Smith" not in summary


def test_summarise_report_handles_errors():
    report = make_report("Test Team", error="Failed to fetch")
    assert summarise_report(report) == "Test Team: Failed to fetch."


def test_summarise_reports_combines_multiple_reports():
    table = DataTable(headers=["Player", "Status", "Injury"], rows=[["A", "Out", "Knee"]])
    report1 = make_report("Team A", table)
    report2 = make_report("Team B", error="No results")

    combined = summarise_reports([report1, report2])
    assert "Team A" in combined
    assert "Team B" in combined
