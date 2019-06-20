# coding=utf-8
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from vault import mail


def send_password_reset_email(user_source):
    token = user_source.get_reset_password_token()
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Volstead\'s Vault Password Reset'
    msg['From'] = os.getenv('MAIL_DEFAULT_SENDER')
    msg['To'] = user_source.email

    text = render_template('email/reset_password.txt', user=user_source, token=token)
    html = render_template('email/reset_password.html', user=user_source, token=token)

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    smtp.sendmail(os.getenv('MAIL_DEFAULT_SENDER'), user_source.email, msg.as_string())

def send_async_email(target_app, msg):
    with target_app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()


def send_mail(subject, sender, recipients, text_body, html_body, attachments=None, sync=False):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    Thread(target=send_async_email, args=(current_app.get_current_object(), msg)).start()