"""Helpers that condense raw injury tables into human readable summaries."""

from __future__ import annotations

import logging
from typing import Iterable, List

from .scraper import ScrapedReport

logger = logging.getLogger(__name__)

PRIORITY_STATUSES = {
    "out",
    "doubtful",
    "questionable",
    "injured reserve",
    "pup",
    "did not practice",
}


def _normalise_column(column_name: str) -> str:
    return column_name.strip().lower().replace("_", " ")


def _find_column(columns: Iterable[str], *candidates: str) -> str | None:
    normalised = {_normalise_column(col): col for col in columns}
    for candidate in candidates:
        candidate = candidate.lower()
        if candidate in normalised:
            return normalised[candidate]
    return None


def summarise_report(report: ScrapedReport) -> str:
    """Produce a human readable summary string for a single team's report."""

    logger.debug(
        "Summarising report",
        extra={"team": report.team_name, "has_tables": bool(report.tables), "error": report.error},
    )
    if report.error:
        return f"{report.team_name}: {report.error}."
    if not report.tables:
        return f"{report.team_name}: No tabular injury information discovered."

    highlights: List[str] = []

    for table in report.tables:
        columns = table.column_names()
        logger.debug(
            "Processing table for summary",
            extra={"team": report.team_name, "columns": columns},
        )
        player_col = _find_column(columns, "player", "name", "athlete")
        status_col = _find_column(columns, "status", "game status")
        injury_col = _find_column(columns, "injury", "reason")

        if not player_col or not status_col:
            logger.debug(
                "Skipping table due to missing columns",
                extra={
                    "team": report.team_name,
                    "player_col": player_col,
                    "status_col": status_col,
                },
            )
            continue

        player_index = columns.index(player_col)
        status_index = columns.index(status_col)
        injury_index = columns.index(injury_col) if injury_col else None

        for row in table.rows:
            player = str(row[player_index]).strip() if player_index < len(row) else ""
            status = str(row[status_index]).strip() if status_index < len(row) else ""
            injury = (
                str(row[injury_index]).strip()
                if injury_index is not None and injury_index < len(row)
                else ""
            )

            if not player or not status:
                logger.debug(
                    "Skipping row missing player or status",
                    extra={"team": report.team_name, "row": row},
                )
                continue

            status_key = status.lower()
            if PRIORITY_STATUSES and not any(k in status_key for k in PRIORITY_STATUSES):
                logger.debug(
                    "Skipping row with non-priority status",
                    extra={"team": report.team_name, "row": row},
                )
                continue

            if injury:
                highlight = f"{player} ({injury}) - {status}"
            else:
                highlight = f"{player} - {status}"
            highlights.append(highlight)

    if highlights:
        joined = "; ".join(highlights[:6])
        if len(highlights) > 6:
            joined += "; …"
        logger.debug(
            "Generated priority injury highlights",
            extra={"team": report.team_name, "highlight_count": len(highlights)},
        )
        return f"{report.team_name}: {joined}."

    logger.debug(
        "No high priority injuries detected",
        extra={"team": report.team_name},
    )
    return f"{report.team_name}: No high priority injuries detected in scraped tables."


def summarise_reports(reports: Iterable[ScrapedReport]) -> str:
    """Combine the summaries for a collection of reports into a single block."""

    logger.debug("Summarising multiple reports")
    return "\n".join(summarise_report(report) for report in reports)


__all__ = ["summarise_report", "summarise_reports"]
