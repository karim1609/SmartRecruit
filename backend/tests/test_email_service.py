import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService, EmailServiceError


def test_render_base_and_test_template():
    service = EmailService()
    html = service.render_template(
        "emails/test_email.html",
        {
            "recipient_name": "Alice Developer",
            "sent_at": "2026-11-21 12:00:00 UTC",
        },
    )
    assert "SmartRecruit" in html
    assert "Alice Developer" in html
    assert "Email Delivery Test" in html
    assert "2026-11-21 12:00:00 UTC" in html


def test_render_verification_code_template():
    service = EmailService()
    html = service.render_template(
        "emails/verification_code.html",
        {
            "full_name": "Bob Candidate",
            "code": "849201",
            "expire_minutes": 15,
        },
    )
    assert "Bob Candidate" in html
    assert "849201" in html
    assert "15 minutes" in html
    assert "Verify Your Email Address" in html


@pytest.mark.asyncio
async def test_send_email_calls_aiosmtplib():
    service = EmailService()
    with patch("aiosmtplib.send") as mock_send:
        await service.send_email(
            to_email="candidate@test.com",
            subject="Test Subject",
            html_content="<p>Test</p>",
            text_content="Test",
        )
        assert mock_send.called
        args, kwargs = mock_send.call_args
        msg = args[0]
        assert msg["Subject"] == "Test Subject"
        assert msg["To"] == "candidate@test.com"


@pytest.mark.asyncio
async def test_send_application_confirmation():
    service = EmailService()
    with patch.object(service, "send_email", new_callable=pytest.importorskip("unittest.mock").AsyncMock) as mock_send:
        await service.send_application_confirmation(
            to_email="candidate@test.com",
            candidate_name="Jane Doe",
            job_title="Full Stack Python Engineer",
            company_name="Acme Corp",
        )
        assert mock_send.called
        kwargs = mock_send.call_args[1]
        assert kwargs["to_email"] == "candidate@test.com"
        assert "Application Received: Full Stack Python Engineer" in kwargs["subject"]
        assert "Acme Corp" in kwargs["html_content"]
        assert "Jane Doe" in kwargs["html_content"]

