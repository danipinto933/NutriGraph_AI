import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings

logger = logging.getLogger(__name__)

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
        return settings.SMTP_PASSWORD

    @property
    def from_email(self) -> str:
        return settings.EMAIL_FROM or settings.SMTP_USER

    @property
    def frontend_url(self) -> str:
        return settings.FRONTEND_URL.rstrip('/')

    def _send_email_smtp_sync(self, to_email: str, subject: str, html_content: str) -> bool:
        try:
            to_email_clean = to_email.strip().lower()
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"NutriGraph AI <{self.from_email}>"
            msg["To"] = to_email_clean
            msg["Reply-To"] = self.from_email

            part = MIMEText(html_content, "html")
            msg.attach(part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, [to_email_clean], msg.as_string())

            logger.info(f"Verification email sent successfully via SMTP to recipient '{to_email_clean}' from '{self.from_email}'")
            return True
        except Exception as e:
            logger.error(f"Error sending email via SMTP to recipient '{to_email}': {e}")
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

email_service = EmailService()
