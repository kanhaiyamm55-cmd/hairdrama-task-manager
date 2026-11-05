
import os
import smtplib
from email.message import EmailMessage


def send_email(to_email, subject, body):
    sender_email = os.getenv("GMAIL_SENDER")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        print("Gmail configuration missing.")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(message)

        print(f"Email sent successfully to {to_email}")
        return True

    except Exception as error:
        print(f"Email sending failed: {error}")
        return False
