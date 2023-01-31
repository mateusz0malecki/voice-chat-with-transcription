from settings import get_settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

app_settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=app_settings.mail_username,
    MAIL_PASSWORD=app_settings.mail_password,
    MAIL_FROM=app_settings.mail_from,
    MAIL_PORT=app_settings.mail_port,
    MAIL_SERVER=app_settings.mail_server,
    MAIL_TLS=app_settings.mail_tls,
    MAIL_SSL=app_settings.mail_ssl,
    USE_CREDENTIALS=app_settings.use_credentials,
    VALIDATE_CERTS=app_settings.validate_certs
)


async def send_email_reset_password(email: list, reset_code: str):
    reset_subject = "Reset password to Digimonkeys"
    recipient = email
    msg = f"""
        Someone requested a link to reset your password. If it wasn't you, please ignore this email.
        
        http://{app_settings.domain}/reset-password?reset_token={reset_code}
        
        Your password won't change until you access the link and create a new one.
        The link has expiry time so do not wait to long to hit it!
    """

    message = MessageSchema(
        subject=reset_subject,
        recipients=recipient,
        body=msg
    )

    fm = FastMail(conf)
    await fm.send_message(message)
