"""Email inbox ingestion — polls IMAP inbox for newsletters."""

import email
import imaplib
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source
from app.models.raw_content import RawContent

logger = logging.getLogger(__name__)


class EmailIngester:
    def __init__(self, imap_server: str, email_addr: str, password: str):
        self.imap_server = imap_server
        self.email_addr = email_addr
        self.password = password

    def _extract_text_from_email(self, msg: email.message.Message) -> str:
        """Extract text content from email message."""
        text_parts = []
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        text_parts.append(payload.decode("utf-8", errors="replace"))
                elif content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        # Basic HTML stripping — for production, use beautifulsoup
                        import re
                        html = payload.decode("utf-8", errors="replace")
                        text = re.sub(r"<[^>]+>", " ", html)
                        text = re.sub(r"\s+", " ", text).strip()
                        text_parts.append(text)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                text_parts.append(payload.decode("utf-8", errors="replace"))

        return "\n".join(text_parts)

    async def ingest_emails(self, db: AsyncSession, source: Source) -> int:
        """Fetch unread emails from inbox and store as raw content."""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_addr, self.password)
            mail.select("INBOX")

            _, message_numbers = mail.search(None, "UNSEEN")
            total_new = 0

            for num in message_numbers[0].split():
                _, msg_data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                subject = msg.get("Subject", "No Subject")
                sender = msg.get("From", "Unknown")
                content = self._extract_text_from_email(msg)

                if content:
                    raw = RawContent(
                        source_id=source.id,
                        title=subject,
                        url="",
                        content_markdown=content[:50000],
                        author=sender,
                        ingested_at=datetime.now(timezone.utc),
                    )
                    db.add(raw)
                    total_new += 1

                # Mark as read
                mail.store(num, "+FLAGS", "\\Seen")

            mail.logout()
            await db.commit()
            logger.info(f"Email ingestion: {total_new} new newsletters")
            return total_new

        except Exception as e:
            logger.error(f"Email ingestion error: {e}")
            return 0
