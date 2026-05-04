import os
import smtplib
from email.message import EmailMessage


def send_reset_email(to_email: str, code: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg = EmailMessage()
    msg["Subject"] = "Monster Ate My Homework Password Reset Code"
    msg["From"] = smtp_user
    msg["To"] = to_email

    msg.set_content(f"""
Your password reset code is:

{code}

This code will expire in 10 minutes.
""")

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)