"""Utilities for formatting and emailing the collected injury data."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Iterable

from .scraper import ScrapedReport
from .summarizer import summarise_reports


class InjuryReportEmailer:
    """Compose and send the injury report email."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str | None,
        smtp_password: str | None,
        sender: str,
        recipients: Iterable[str],
        use_tls: bool = True,
    ) -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.sender = sender
        self.recipients = list(recipients)
        self.use_tls = use_tls

    @classmethod
    def from_environment(cls) -> "InjuryReportEmailer":
        """Create an emailer using configuration stored in environment variables."""

        smtp_host = os.environ.get("SMTP_HOST")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USER")
        smtp_password = os.environ.get("SMTP_PASSWORD")
        sender = os.environ.get("SMTP_SENDER") or smtp_user
        recipients = os.environ.get("INJURY_REPORT_RECIPIENT")

        if not smtp_host or not sender or not recipients:
            raise RuntimeError(
                "SMTP_HOST, SMTP_SENDER/SMTP_USER, and INJURY_REPORT_RECIPIENT must be set"
            )

        recipient_list = [email.strip() for email in recipients.split(",") if email.strip()]
        return cls(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            sender=sender,
            recipients=recipient_list,
            use_tls=True,
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
        """Send a prepared email message using the configured SMTP server."""

        if self.use_tls:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)


__all__ = ["InjuryReportEmailer"]
