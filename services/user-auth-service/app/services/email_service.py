import asyncio
import logging
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings

logger = logging.getLogger(__name__)


class IPv4SMTP(smtplib.SMTP):
    """
    Forces IPv4 (socket.AF_INET) connection to prevent '[Errno 101] Network is unreachable'
    errors on containerized hosting platforms (e.g. Render) where IPv6 DNS entries
    are returned first by getaddrinfo but IPv6 routing is unavailable.
    """
    def _get_socket(self, host, port, timeout):
        res_list = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        err = None
        for res in res_list:
            af, socktype, proto, canonname, sa = res
            sock = None
            try:
                sock = socket.socket(af, socktype, proto)
                if timeout is not None:
                    sock.settimeout(timeout)
                sock.connect(sa)
                return sock
            except Exception as e:
                err = e
                if sock is not None:
                    sock.close()
        if err:
            raise err
        raise OSError(f"Could not connect to {host}:{port} via IPv4")


class IPv4SMTP_SSL(smtplib.SMTP_SSL):
    """
    Forces IPv4 (socket.AF_INET) SSL connection to prevent '[Errno 101] Network is unreachable'
    errors on containerized hosting platforms (e.g. Render).
    """
    def _get_socket(self, host, port, timeout):
        res_list = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        err = None
        for res in res_list:
            af, socktype, proto, canonname, sa = res
            sock = None
            try:
                sock = socket.socket(af, socktype, proto)
                if timeout is not None:
                    sock.settimeout(timeout)
                sock.connect(sa)
                return self.context.wrap_socket(sock, server_hostname=self._host)
            except Exception as e:
                err = e
                if sock is not None:
                    sock.close()
        if err:
            raise err
        raise OSError(f"Could not connect to {host}:{port} via IPv4")


class EmailService:
    @property
    def smtp_host(self) -> str:
        return settings.SMTP_HOST

    @property
    def smtp_port(self) -> int:
        return int(settings.SMTP_PORT)

    @property
    def smtp_user(self) -> str:
        return settings.SMTP_USER

    @property
    def smtp_password(self) -> str:
        raw_pwd = settings.SMTP_PASSWORD or ""
        return raw_pwd.replace(" ", "").strip()

    @property
    def from_email(self) -> str:
        return settings.EMAIL_FROM or settings.SMTP_USER

    @property
    def frontend_url(self) -> str:
        return settings.FRONTEND_URL.rstrip('/')

    def _send_email_smtp_sync(self, to_email: str, subject: str, html_content: str) -> bool:
        to_email_clean = to_email.strip().lower()
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"NutriGraph AI <{self.from_email}>"
        msg["To"] = to_email_clean
        msg["Reply-To"] = self.from_email

        part = MIMEText(html_content, "html")
        msg.attach(part)

        primary_port = self.smtp_port
        fallback_port = 587 if primary_port == 465 else 465
        ports_to_try = [primary_port]
        if fallback_port not in ports_to_try:
            ports_to_try.append(fallback_port)

        last_err = None

        for port in ports_to_try:
            try:
                logger.info(f"Attempting SMTP email delivery (host: {self.smtp_host}, port: {port}, family: IPv4) to '{to_email_clean}'...")
                if port == 465:
                    with IPv4SMTP_SSL(self.smtp_host, port, timeout=12) as server:
                        server.login(self.smtp_user, self.smtp_password)
                        server.sendmail(self.from_email, [to_email_clean], msg.as_string())
                else:
                    with IPv4SMTP(self.smtp_host, port, timeout=12) as server:
                        server.starttls()
                        server.login(self.smtp_user, self.smtp_password)
                        server.sendmail(self.from_email, [to_email_clean], msg.as_string())

                logger.info(f"Email sent successfully via SMTP (port {port}, IPv4) to recipient '{to_email_clean}' from '{self.from_email}'")
                return True
            except smtplib.SMTPAuthenticationError as auth_err:
                logger.error(f"SMTP Auth Failure (Check App Password / SMTP_USER / SMTP_PASSWORD) for recipient '{to_email_clean}': {auth_err}")
                return False
            except Exception as e:
                logger.warning(f"Failed SMTP delivery attempt on port {port} for recipient '{to_email_clean}': {e}")
                last_err = e

        logger.error(f"All SMTP connection attempts failed for recipient '{to_email_clean}'. Last error: {last_err}", exc_info=True)
        return False

    async def send_verification_email(self, to_email: str, first_name: str, verification_token: str) -> bool:
        """
        Sends a magic link email verification using Gmail SMTP.
        """
        to_email_clean = to_email.strip().lower()
        verification_url = f"{self.frontend_url}/verify-email?token={verification_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #0f172a;
                    color: #e2e8f0;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 550px;
                    margin: 40px auto;
                    background: #1e293b;
                    border-radius: 16px;
                    padding: 32px;
                    border: 1px solid #334155;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 24px;
                }}
                .title {{
                    font-size: 26px;
                    font-weight: 700;
                    background: linear-gradient(135deg, #00d2ff 0%, #10b981 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin: 0;
                }}
                .content {{
                    line-height: 1.6;
                    color: #cbd5e1;
                    font-size: 15px;
                }}
                .btn-container {{
                    text-align: center;
                    margin: 32px 0;
                }}
                .btn {{
                    display: inline-block;
                    padding: 14px 32px;
                    background: linear-gradient(135deg, #00d2ff 0%, #10b981 100%);
                    color: #0f172a !important;
                    font-weight: 700;
                    text-decoration: none;
                    border-radius: 8px;
                    font-size: 16px;
                    box-shadow: 0 4px 15px rgba(0, 210, 255, 0.3);
                }}
                .footer {{
                    margin-top: 32px;
                    font-size: 12px;
                    color: #64748b;
                    text-align: center;
                    border-top: 1px solid #334155;
                    padding-top: 16px;
                }}
                .link-text {{
                    word-break: break-all;
                    color: #00d2ff;
                    font-size: 13px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="title">NutriGraph AI</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{first_name}</strong>,</p>
                    <p>¡Gracias por registrarte en NutriGraph AI! Para completar tu registro y asegurar que tu cuenta esté protegida contra accesos no autorizados o bots, confirma tu dirección de correo electrónico haciendo clic en el siguiente botón:</p>
                    
                    <div class="btn-container">
                        <a href="{verification_url}" class="btn">Verificar mi Cuenta</a>
                    </div>
                    
                    <p>Este enlace de activación caducará en <strong>30 minutos</strong>.</p>
                    <p>Si el botón no funciona, copia y pega el siguiente enlace en tu navegador:</p>
                    <p class="link-text">{verification_url}</p>
                </div>
                <div class="footer">
                    <p>Si no creaste una cuenta en NutriGraph AI, puedes ignorar este correo con seguridad.</p>
                    <p>&copy; 2026 NutriGraph AI - Plataforma de Nutrición Inteligente</p>
                </div>
            </div>
        </body>
        </html>
        """

        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials are not configured. Skipping email sending.")
            return False

        subject = "Verifica tu cuenta en NutriGraph AI - Magic Link"
        return await asyncio.to_thread(self._send_email_smtp_sync, to_email_clean, subject, html_content)

    async def send_admin_notification(self, registered_user_email: str, first_name: str) -> bool:
        """
        Sends an alert email to the admin when a new user registers or requests access.
        """
        admin_email = getattr(settings, "ADMIN_EMAIL", "danipinto933@gmail.com")
        if not admin_email:
            logger.warning("No ADMIN_EMAIL specified. Skipping admin notification.")
            return False

        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured. Skipping admin notification email.")
            return False

        subject = f"🔔 Nuevo usuario registrado en NutriGraph AI: {registered_user_email}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }}
                .container {{ max-width: 550px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 32px; border: 1px solid #334155; }}
                .title {{ font-size: 22px; font-weight: 700; color: #10b981; margin-top: 0; }}
                .info-box {{ background: #0f172a; border-radius: 8px; padding: 16px; margin: 20px 0; border-left: 4px solid #00d2ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2 class="title">🔔 Nueva Solicitud de Registro</h2>
                <p>Se ha registrado un nuevo usuario en la plataforma NutriGraph AI:</p>
                <div class="info-box">
                    <p><strong>Nombre:</strong> {first_name}</p>
                    <p><strong>Correo electrónico:</strong> {registered_user_email}</p>
                    <p><strong>Estado:</strong> Pendiente de verificación por correo electrónico</p>
                </div>
                <p style="font-size: 13px; color: #94a3b8;">Notificación automática del sistema NutriGraph AI.</p>
            </div>
        </body>
        </html>
        """
        return await asyncio.to_thread(self._send_email_smtp_sync, admin_email.strip().lower(), subject, html_content)

email_service = EmailService()
