"""Utilities for collecting injury reports using headless Chrome."""

from __future__ import annotations

import logging
import os
import subprocess
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable, List, Optional
from urllib.parse import quote_plus, unquote

from .teams import build_search_query, build_team_injury_url

logger = logging.getLogger(__name__)

GOOGLE_SEARCH_URL = "https://www.google.com/search?q={query}"


@dataclass
class DataTable:
    """A minimal representation of an HTML table."""

    headers: List[str]
    rows: List[List[str]]

    def is_empty(self) -> bool:
        return not self.rows

    def column_names(self) -> List[str]:
        return self.headers

    def to_html(self) -> str:
        header_html = "".join(f"<th>{cell}</th>" for cell in self.headers)
        rows_html = "".join(
            "<tr>" + "".join(f"<td>{value}</td>" for value in row) + "</tr>"
            for row in self.rows
        )
        return (
            "<table class='injury-table'><thead><tr>"
            + header_html
            + "</tr></thead><tbody>"
            + rows_html
            + "</tbody></table>"
        )


@dataclass
class ScrapedReport:
    team_name: str
    url: Optional[str]
    tables: List[DataTable]
    error: Optional[str] = None

    def has_data(self) -> bool:
        return any(not table.is_empty() for table in self.tables)


class ChromeFetcher:
    """Fetch rendered HTML using the Chrome headless command line interface."""

    def __init__(self, binary: str | None = None, timeout: int = 90) -> None:
        self.binary = binary or os.environ.get("CHROME_BINARY", "google-chrome")
        self.timeout = timeout

    def fetch(self, url: str) -> str:
        if not self.binary:
            raise RuntimeError("Chrome binary path is not configured")

        logger.debug("Fetching URL with Chrome", extra={"url": url, "binary": self.binary})
        command = [
            self.binary,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--virtual-time-budget=10000",
            "--dump-dom",
            url,
        ]

        try:
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
            )
        except FileNotFoundError as exc:  # pragma: no cover - configuration issue
            raise RuntimeError(
                f"Chrome binary '{self.binary}' not found. Set CHROME_BINARY to the correct path."
            ) from exc
        except subprocess.CalledProcessError as exc:
            logger.debug("Chrome subprocess failed", extra={"url": url, "stderr": exc.stderr})
            raise RuntimeError(f"Chrome failed: {exc.stderr.strip() or exc}") from exc
        except subprocess.TimeoutExpired as exc:
            logger.debug("Chrome subprocess timed out", extra={"url": url, "timeout": self.timeout})
            raise RuntimeError(f"Chrome timed out fetching {url}") from exc

        return result.stdout


class _GoogleResultParser(HTMLParser):
    """Extract the first organic link from Google search results."""

    def __init__(self) -> None:
        super().__init__()
        self.first_url: Optional[str] = None

    def handle_starttag(self, tag: str, attrs):  # type: ignore[override]
        if self.first_url or tag != "a":
            return
        attr_map = dict(attrs)
        href = attr_map.get("href")
        if not href:
            return
        if href.startswith("/url?q="):
            candidate = unquote(href[7:]).split("&", 1)[0]
        else:
            candidate = href
        if candidate.startswith("http"):
            self.first_url = candidate


class _HTMLTableParser(HTMLParser):
    """Parse HTML tables into DataTable objects."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: List[DataTable] = []
        self._in_table = False
        self._headers: List[str] = []
        self._rows: List[List[str]] = []
        self._current_row: List[str] = []
        self._current_cell: List[str] = []
        self._in_header_cell = False

    def handle_starttag(self, tag: str, attrs):  # type: ignore[override]
        if tag == "table":
            if self._in_table:
                return
            self._in_table = True
            self._headers = []
            self._rows = []
        elif self._in_table and tag == "tr":
            self._current_row = []
        elif self._in_table and tag in {"td", "th"}:
            self._current_cell = []
            self._in_header_cell = tag == "th"

    def handle_data(self, data: str):  # type: ignore[override]
        if self._in_table and self._current_cell is not None:
            self._current_cell.append(data.strip())

    def handle_endtag(self, tag: str):  # type: ignore[override]
        if tag == "table" and self._in_table:
            if self._headers or self._rows:
                headers = self._headers or [f"Column {i+1}" for i in range(len(self._rows[0]) if self._rows else 0)]
                self.tables.append(DataTable(headers=headers, rows=self._rows))
            self._in_table = False
        elif self._in_table and tag == "tr":
            if self._current_row:
                if not self._headers:
                    self._headers = self._current_row
                else:
                    self._rows.append(self._current_row)
            self._current_row = []
        elif self._in_table and tag in {"td", "th"}:
            cell_text = " ".join(part for part in self._current_cell if part)
            self._current_row.append(cell_text.strip())
            self._current_cell = []


class InjuryReportScraper:
    """Scrape team injury reports by querying Google with headless Chrome."""

    def __init__(self, fetcher: ChromeFetcher | None = None) -> None:
        self.fetcher = fetcher or ChromeFetcher()

    def _navigate_to_first_result(self, html: str) -> Optional[str]:
        parser = _GoogleResultParser()
        parser.feed(html)
        logger.debug("Parsed Google results", extra={"first_url": parser.first_url})
        return parser.first_url

    def _extract_tables(self, html: str) -> List[DataTable]:
        parser = _HTMLTableParser()
        parser.feed(html)
        logger.debug(
            "Extracted tables from HTML",
            extra={"table_count": len(parser.tables)},
        )
        return parser.tables

    def _detect_missing_table_reason(self, html: str) -> Optional[str]:
        lowered = html.lower()
        phrases = [
            "no injury report",
            "no injuries to report",
            "injury report is not yet available",
        ]
        for phrase in phrases:
            if phrase in lowered:
                reason = "Injury report not published for this week"
                logger.debug("Detected missing injury table notice", extra={"phrase": phrase})
                return reason
        return None

    def _scrape_direct_team_page(self, team_name: str) -> ScrapedReport | None:
        direct_url = build_team_injury_url(team_name)
        if direct_url is None:
            logger.debug("No direct injury URL for team", extra={"team": team_name})
            return None

        try:
            page_html = self.fetcher.fetch(direct_url)
        except Exception:  # pragma: no cover - defensive fallback
            logger.debug(
                "Direct fetch failed, falling back to Google",
                exc_info=True,
                extra={"team": team_name, "url": direct_url},
            )
            return None

        tables = self._extract_tables(page_html)
        if not tables:
            reason = self._detect_missing_table_reason(page_html)
            if reason:
                logger.debug(
                    "Direct page indicates no injury report",
                    extra={"team": team_name, "url": direct_url},
                )
                return ScrapedReport(team_name=team_name, url=direct_url, tables=[], error=reason)
            logger.debug(
                "No tables found on direct page",
                extra={"team": team_name, "url": direct_url},
            )
            return None

        return ScrapedReport(team_name=team_name, url=direct_url, tables=tables)

    def _scrape_via_google(self, team_name: str) -> ScrapedReport:
        query = build_search_query(team_name)
        search_url = GOOGLE_SEARCH_URL.format(query=quote_plus(query))
        logger.debug(
            "Fetching Google search results",
            extra={"team": team_name, "query": query, "search_url": search_url},
        )
        search_html = self.fetcher.fetch(search_url)
        target_url = self._navigate_to_first_result(search_html)

        if not target_url:
            logger.debug(
                "No Google result found",
                extra={"team": team_name, "query": query},
            )
            return ScrapedReport(team_name=team_name, url=None, tables=[], error="No results")

        logger.debug(
            "Fetching injury page from Google result",
            extra={"team": team_name, "target_url": target_url},
        )
        page_html = self.fetcher.fetch(target_url)
        tables = self._extract_tables(page_html)

        if not tables:
            reason = self._detect_missing_table_reason(page_html)
            if reason:
                logger.debug(
                    "Google result indicates no injury report",
                    extra={"team": team_name, "url": target_url},
                )
                return ScrapedReport(
                    team_name=team_name,
                    url=target_url,
                    tables=[],
                    error=reason,
                )
            return ScrapedReport(
                team_name=team_name,
                url=target_url,
                tables=[],
                error="No tabular injury data found",
            )
        return ScrapedReport(team_name=team_name, url=target_url, tables=tables)

    def search(self, team_name: str) -> ScrapedReport:
        logger.debug("Searching for team injury report", extra={"team": team_name})
        direct_report = self._scrape_direct_team_page(team_name)
        if direct_report is not None:
            logger.debug(
                "Using direct report",
                extra={"team": team_name, "url": direct_report.url, "error": direct_report.error},
            )
            return direct_report
        logger.debug("Falling back to Google search", extra={"team": team_name})
        return self._scrape_via_google(team_name)

    def scrape_many(self, teams: Iterable[str]) -> List[ScrapedReport]:
        results: List[ScrapedReport] = []
        for team in teams:
            try:
                report = self.search(team)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.debug(
                    "Scraping failed for team",
                    exc_info=True,
                    extra={"team": team},
                )
                report = ScrapedReport(team_name=team, url=None, tables=[], error=str(exc))
            results.append(report)
            time.sleep(0.3)
        logger.debug("Completed scraping teams", extra={"team_count": len(results)})
        return results


__all__ = ["ChromeFetcher", "DataTable", "InjuryReportScraper", "ScrapedReport"]
