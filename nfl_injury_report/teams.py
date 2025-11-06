"""Definitions of NFL team names used by the injury report scraper."""

from __future__ import annotations

from datetime import date

NFL_TEAMS = [
    "Arizona Cardinals",
    "Atlanta Falcons",
    "Baltimore Ravens",
    "Buffalo Bills",
    "Carolina Panthers",
    "Chicago Bears",
    "Cincinnati Bengals",
    "Cleveland Browns",
    "Dallas Cowboys",
    "Denver Broncos",
    "Detroit Lions",
    "Green Bay Packers",
    "Houston Texans",
    "Indianapolis Colts",
    "Jacksonville Jaguars",
    "Kansas City Chiefs",
    "Las Vegas Raiders",
    "Los Angeles Chargers",
    "Los Angeles Rams",
    "Miami Dolphins",
    "Minnesota Vikings",
    "New England Patriots",
    "New Orleans Saints",
    "New York Giants",
    "New York Jets",
    "Philadelphia Eagles",
    "Pittsburgh Steelers",
    "San Francisco 49ers",
    "Seattle Seahawks",
    "Tampa Bay Buccaneers",
    "Tennessee Titans",
    "Washington Commanders",
]


def build_search_query(team_name: str, target_date: date | None = None) -> str:
    """Return the Google search query for the provided team and date.

    Args:
        team_name: Official NFL team name.
        target_date: Optional date. When omitted the current date is used.

    Returns:
        A query string that can be appended to a Google search URL.
    """

    if target_date is None:
        target_date = date.today()
    formatted_date = target_date.strftime("%B %d, %Y")
    return f"{team_name} Injury Report {formatted_date}"


__all__ = ["NFL_TEAMS", "build_search_query"]
