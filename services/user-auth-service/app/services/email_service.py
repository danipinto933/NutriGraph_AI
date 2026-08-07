import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.EMAIL_FROM
        self.frontend_url = settings.FRONTEND_URL

    async def send_verification_email(self, to_email: str, first_name: str, verification_token: str) -> bool:
        """
        Sends a magic link email verification using Resend API.
        """
        if not self.api_key:
            logger.warning("RESEND_API_KEY is not configured. Skipping email sending.")
            return False

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

        payload = {
            "from": self.from_email,
            "to": [to_email],
            "subject": "Verifica tu cuenta en NutriGraph AI - Magic Link",
            "html": html_content
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post("https://api.resend.com/emails", json=payload, headers=headers)
                if response.status_code in [200, 201]:
                    logger.info(f"Verification email sent successfully via Resend to {to_email}")
                    return True
                else:
                    logger.error(f"Failed to send email via Resend: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending email via Resend API: {e}")
            return False

email_service = EmailService()
