import smtplib
from email.mime.text import MIMEText
from config import Config

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = Config.SMTP_FROM
    msg["To"] = to_email

    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
        if Config.SMTP_USER and Config.SMTP_PASS:
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASS)
        server.send_message(msg)
