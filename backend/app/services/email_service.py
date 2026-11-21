import logging
import os
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Mapping

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger(__name__)

# Base templates directory path
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


class EmailServiceError(Exception):
    """Base exception for email service errors."""
    pass


class EmailService:
    """Service handling template rendering and asynchronous email dispatch."""

    def __init__(self, template_dir: str = TEMPLATES_DIR) -> None:
        self.template_dir = template_dir
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_template(self, template_name: str, context: Mapping[str, Any]) -> str:
        """Render a Jinja2 template with provided context."""
        template_context = dict(context)
        template_context.setdefault("current_year", datetime.now(timezone.utc).year)
        template_context.setdefault("app_name", settings.APP_NAME)
        template = self.jinja_env.get_template(template_name)
        return template.render(**template_context)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> None:
        """Send an HTML email asynchronously via SMTP (aiosmtplib)."""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        message["To"] = to_email

        # Attach fallback plain text if provided
        if text_content:
            message.attach(MIMEText(text_content, "plain", "utf-8"))

        # Attach HTML body
        message.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS,
                start_tls=settings.SMTP_STARTTLS,
                timeout=10,
            )
            logger.info("Email '%s' sent successfully to %s", subject, to_email)
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", to_email, str(exc))
            raise EmailServiceError(f"Email delivery failed: {exc}") from exc

    async def send_test_email(self, to_email: str, recipient_name: str = "User") -> None:
        """Send a test email for health checks and verification."""
        sent_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        html = self.render_template(
            "emails/test_email.html",
            {
                "recipient_name": recipient_name,
                "sent_at": sent_at,
            },
        )
        await self.send_email(
            to_email=to_email,
            subject=f"[{settings.APP_NAME}] Email Delivery Test",
            html_content=html,
            text_content=f"Email delivery test sent to {recipient_name} at {sent_at}.",
        )

    async def send_verification_email(
        self,
        to_email: str,
        full_name: str,
        code: str,
        expire_minutes: int | None = None,
    ) -> None:
        """Send account verification 6-digit code."""
        if expire_minutes is None:
            expire_minutes = settings.VERIFICATION_CODE_EXPIRE_MINUTES

        html = self.render_template(
            "emails/verification_code.html",
            {
                "full_name": full_name,
                "code": code,
                "expire_minutes": expire_minutes,
            },
        )
        await self.send_email(
            to_email=to_email,
            subject=f"[{settings.APP_NAME}] Your Verification Code: {code}",
            html_content=html,
            text_content=f"Hello {full_name},\nYour SmartRecruit verification code is: {code}\nThis code expires in {expire_minutes} minutes.",
        )

    async def send_application_confirmation(
        self,
        to_email: str,
        candidate_name: str,
        job_title: str,
        company_name: str,
    ) -> None:
        """Send job application confirmation email to candidate."""
        applied_at = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
        html = self.render_template(
            "emails/application_confirmation.html",
            {
                "candidate_name": candidate_name,
                "job_title": job_title,
                "company_name": company_name,
                "applied_at": applied_at,
            },
        )
        plain_text = (
            f"Hello {candidate_name},\n\n"
            f"We have received your application for '{job_title}' at '{company_name}'.\n"
            f"Our recruitment team is reviewing your profile and will contact you regarding next steps.\n"
            f"You can track the progress of your application in your candidate dashboard.\n\n"
            f"Submitted on: {applied_at}\n\n"
            f"Best regards,\nSmartRecruit Team"
        )
        await self.send_email(
            to_email=to_email,
            subject=f"[{settings.APP_NAME}] Application Received: {job_title}",
            html_content=html,
            text_content=plain_text,
        )


# Singleton instance
email_service = EmailService()
