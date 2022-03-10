from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.message import EmailMessage
from email import encoders
import smtplib
import os
import json

# Email credentials
email = "testingsendingemails111@gmail.com"
password = "PetrHanzl123"

# Path to message template
html_body_template = "docs/email-format.html"


# Sends email with verification token
def send_mail(receiver, token):

    with open(html_body_template, "r") as f:
        template = f.read()

    # SMTP server for email service
    server = smtplib.SMTP_SSL("smtp.gmail.com")
    server.login(email, password)

    # Creating a message
    html = template.replace("{tokenplaceholder}", str(token))
    text = "Here is your verification code: " + str(token)
    message = MIMEMultipart()
    message["Subject"] = "MENDELU Discord Verification"
    # This doesnt seem to work
    message["From"] = "bot@mendeludiscord.com"
    message["To"] = receiver

    # Attaching the text to a message
    message.attach(MIMEText(html, "html"))
    message.attach(MIMEText(text, "plain"))

    # Finally, sending a message with the token
    str_msg = message.as_string()
    server.sendmail(email, receiver, str_msg)
