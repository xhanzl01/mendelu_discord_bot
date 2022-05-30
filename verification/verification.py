import os

from config import email, password
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import date
import logging
import requests

# Path to message template
html_body_template = "docs/email-format.html"


# Sends email with verification token
def send_mail(receiver, token):
    with open(html_body_template, "r") as f:
        template = f.read()

    # SMTP server for email service
    server = smtplib.SMTP_SSL("smtp.seznam.cz")
    server.login(email, password)

    # Creating a message
    html = template.replace("{tokenplaceholder}", str(token))
    text = "Here is your verification code: " + str(token)
    message = MIMEMultipart()
    message["Subject"] = "MENDELU Discord Verification"
    message["From"] = "bot@mendeludiscord.com"
    message["To"] = receiver

    # Attaching the text to a message
    message.attach(MIMEText(html, "html"))
    message.attach(MIMEText(text, "plain"))

    # Finally, sending a message with the token
    str_msg = message.as_string()
    server.sendmail(email, receiver, str_msg)
    logging.info(f"E-mail with token {token} sent to {receiver}")


def is_valid_student(uid):
    r = requests.get("https://is.mendelu.cz/karty/platnost.pl?cislo=" + str(uid) + ";datum="
                     + date.strftime(date.today(), "%d.%m.%Y") + ";lang=cz")
    if "ano" in r.text:
        return "john doe"
    return


def is_valid_email(mail):
    if (mail[0] == "x" or mail[0] == "qq") and mail.split("@")[1] == "mendelu.cz":
        return True
    else:
        return False


async def check_token(token):
    return token == token
