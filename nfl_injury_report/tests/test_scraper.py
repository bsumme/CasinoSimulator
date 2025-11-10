from __future__ import annotations

from typing import Dict, List

import pytest

from nfl_injury_report.scraper import GOOGLE_SEARCH_URL, DataTable, InjuryReportScraper


class StubFetcher:
    def __init__(self, responses: Dict[str, List[str]]) -> None:
        self.responses = {url: list(payloads) for url, payloads in responses.items()}
        self.calls: List[str] = []

    def fetch(self, url: str) -> str:
        self.calls.append(url)
        try:
            payloads = self.responses[url]
        except KeyError as exc:  # pragma: no cover - unexpected fetch
            raise AssertionError(f"Unexpected fetch for URL: {url}") from exc
        if not payloads:
            raise AssertionError(f"No more stubbed responses for URL: {url}")
        return payloads.pop(0)


TABLE_HTML = """
<html>
  <body>
    <table>
      <tr><th>Player</th><th>Status</th><th>Injury</th></tr>
      <tr><td>John Doe</td><td>Out</td><td>Shoulder</td></tr>
    </table>
  </body>
</html>
"""


def make_google_results(url: str) -> str:
    return f'<a href="/url?q={url}">Result</a>'


def test_scraper_prefers_direct_team_page(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nfl_injury_report.scraper.build_search_query",
        lambda _: "unused",
    )
    direct_url = "https://www.nfl.com/teams/new-orleans-saints/injuries/"
    fetcher = StubFetcher({direct_url: [TABLE_HTML]})

    scraper = InjuryReportScraper(fetcher=fetcher)
    report = scraper.search("New Orleans Saints")

    assert report.url == direct_url
    assert report.tables and isinstance(report.tables[0], DataTable)
    assert fetcher.calls == [direct_url]


def test_scraper_falls_back_to_google_when_direct_has_no_tables(monkeypatch: pytest.MonkeyPatch) -> None:
    target_url = "https://example.com/injuries"
    google_query = "Saints Injury Query"
    monkeypatch.setattr(
        "nfl_injury_report.scraper.build_search_query",
        lambda _: google_query,
    )
    direct_url = "https://www.nfl.com/teams/new-orleans-saints/injuries/"
    search_url = GOOGLE_SEARCH_URL.format(query="Saints+Injury+Query")

    fetcher = StubFetcher(
        {
            direct_url: ["<html></html>"],
            search_url: [make_google_results(target_url)],
            target_url: [TABLE_HTML],
        }
    )

    scraper = InjuryReportScraper(fetcher=fetcher)
    report = scraper.search("New Orleans Saints")

    assert report.url == target_url
    assert report.tables and isinstance(report.tables[0], DataTable)
    assert fetcher.calls == [direct_url, search_url, target_url]
