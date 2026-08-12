from unittest.mock import MagicMock, patch
import pytest
from app.services.email_service import EmailService, IPv4SMTP


@pytest.mark.asyncio
async def test_email_service_fallback_ports():
    email_service = EmailService()
    
    with patch("app.services.email_service.settings") as mock_settings, \
         patch("app.services.email_service.IPv4SMTP_SSL") as mock_ssl, \
         patch("app.services.email_service.IPv4SMTP") as mock_smtp:
        
        mock_settings.SMTP_PORT = 465
        mock_settings.SMTP_HOST = "smtp.gmail.com"
        mock_settings.SMTP_USER = "user@test.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.EMAIL_FROM = "user@test.com"
        
        # Primary port 465 fails, fallback port 587 succeeds
        mock_ssl.side_effect = Exception("Port 465 network unreachable")
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        result = email_service._send_email_smtp_sync(
            "test@example.com",
            "Subject Test",
            "<p>Test</p>"
        )
        
        assert result is True
        assert mock_ssl.called
        assert mock_smtp.called


@pytest.mark.asyncio
async def test_ipv4_socket_creation_mock():
    with patch("socket.getaddrinfo") as mock_getaddrinfo, \
         patch("socket.socket") as mock_socket:
        
        mock_getaddrinfo.return_value = [
            (2, 1, 6, "", ("142.251.16.108", 587))
        ]
        
        mock_file = MagicMock()
        mock_file.readline.side_effect = [b"220 smtp.gmail.com ESMTP\r\n", b"250-smtp.gmail.com\r\n", b"250 OK\r\n"]
        
        mock_sock_inst = MagicMock()
        mock_sock_inst.makefile.return_value = mock_file
        mock_socket.return_value = mock_sock_inst
        
        smtp = IPv4SMTP("smtp.gmail.com", 587, timeout=5)
        assert smtp is not None
