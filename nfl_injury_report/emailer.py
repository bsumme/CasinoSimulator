"""Utilities for formatting and emailing the collected injury data."""

from __future__ import annotations

import json
import os
from email.message import EmailMessage
from http.client import HTTPSConnection
from typing import Iterable

from .scraper import ScrapedReport
from .summarizer import summarise_reports


class InjuryReportEmailer:
    """Compose and send the injury report email."""

    def __init__(
        self,
        api_key: str,
        sender: str,
        recipients: Iterable[str],
    ) -> None:
        self.api_key = api_key
        self.sender = sender
        self.recipients = list(recipients)

    @classmethod
    def from_environment(cls) -> "InjuryReportEmailer":
        """Create an emailer using configuration stored in environment variables."""

        api_key = os.environ.get("SENDGRID_API_KEY")
        sender = os.environ.get("SENDGRID_SENDER")
        recipients = os.environ.get("INJURY_REPORT_RECIPIENT")

        if not api_key or not sender or not recipients:
            raise RuntimeError(
                "SENDGRID_API_KEY, SENDGRID_SENDER, and INJURY_REPORT_RECIPIENT must be set"
            )

        recipient_list = [email.strip() for email in recipients.split(",") if email.strip()]
        return cls(
            api_key=api_key,
            sender=sender,
            recipients=recipient_list,
        )

    @staticmethod
    def _format_tables_html(reports: Iterable[ScrapedReport]) -> str:
        """Return an HTML string representing all gathered tables."""

        sections: list[str] = []
        for report in reports:
            if not report.tables:
                continue
            rendered_tables = "".join(table.to_html() for table in report.tables)
            sections.append(f"<h3>{report.team_name}</h3>{rendered_tables}")

        if not sections:
            return "<p>No tabular injury data was captured.</p>"

        style = (
            "<style>.injury-table{border-collapse:collapse;width:100%;margin-bottom:16px;}"
            ".injury-table th,.injury-table td{border:1px solid #ccc;padding:6px;text-align:left;}"
            ".injury-table th{background:#f5f5f5;}</style>"
        )
        return style + "".join(sections)

    def build_email(self, reports: Iterable[ScrapedReport]) -> EmailMessage:
        """Build the email message summarising the injury reports."""

        reports = list(reports)
        summary_text = summarise_reports(reports)
        html_tables = self._format_tables_html(reports)

        message = EmailMessage()
        message["Subject"] = "Daily NFL Injury Report"
        message["From"] = self.sender
        message["To"] = ", ".join(self.recipients)
        message.set_content(summary_text)
        message.add_alternative(
            f"<html><body><pre>{summary_text}</pre>{html_tables}</body></html>",
            subtype="html",
        )
        return message

    def send_email(self, message: EmailMessage) -> None:
        """Send a prepared email message using the SendGrid API."""

        plain_body = message.get_body(preferencelist=("plain",))
        html_body = message.get_body(preferencelist=("html",))

        content = []
        if plain_body is not None:
            content.append({"type": "text/plain", "value": plain_body.get_content()})
        if html_body is not None:
            content.append({"type": "text/html", "value": html_body.get_content()})

        if not content:
            content.append({"type": "text/plain", "value": message.get_content()})

        payload = {
            "personalizations": [
                {"to": [{"email": recipient} for recipient in self.recipients]}
            ],
            "from": {"email": self.sender},
            "subject": message["Subject"],
            "content": content,
        }

        connection = HTTPSConnection("api.sendgrid.com")
        try:
            connection.request(
                "POST",
                "/v3/mail/send",
                body=json.dumps(payload),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            response = connection.getresponse()
            response.read()  # Ensure the connection can be reused/closed cleanly.
            if response.status >= 400:
                raise RuntimeError(
                    "Failed to send email via SendGrid API: "
                    f"{response.status} {response.reason}"
                )
        finally:
            connection.close()


__all__ = ["InjuryReportEmailer"]
