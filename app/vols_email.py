
# (venv) $ python -m smtpd -n -c DebuggingServer localhost:8025
# (venv) $ export MAIL_SERVER=localhost
# (venv) $ export MAIL_PORT=8025
# (venv) $ export MAIL_SERVER=smtp.googlemail.com
# (venv) $ export MAIL_PORT=587
# (venv) $ export MAIL_USE_TLS=1
# (venv) $ export MAIL_USERNAME=<your-gmail-username>
# (venv) $ export MAIL_PASSWORD=<your-gmail-password>






# coding=utf-8

from threading import Thread
from flask import current_app
from flask_mail import Message

from app import mail
from vol_app import app
from flask import render_template
from config import Config


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Volstead\'s Vault Reset Your Password',
               sender=Config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))

def send_async_email(target_app, msg):
    with target_app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # mail.send(msg)
    Thread(target=send_async_email, args=(app, msg)).start()

def send_mail(subject, sender, recipients, text_body, html_body, attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    Thread(target=send_async_email, args=(current_app.get_current_object(), msg)).start()