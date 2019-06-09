# coding=utf-8
import smtplib
from threading import Thread
from email import message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from flask import current_app, copy_current_request_context
from flask_mail import Message
from . import mail
from flask import render_template

# def send_password_reset_email(user):
#     token = user.get_reset_password_token()
#
#     server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#     server_ssl.ehlo()
#     server_ssl.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))
#
#     msg = Message()
#     msg.subject = '[Volstead\'s Vault Reset Your Password'
#     msg.recipients = [user.email]
#     msg.body = render_template('email/reset_password.txt', user=user, token=token)
#     msg.html = render_template('email/reset_password.html', user=user, token=token)
#
#     server_ssl.sendmail(os.environ.get('USER_EMAIL_SENDER_EMAIL'), user.email, msg)
#     server_ssl.close()

def send_password_reset_email(user_source):
    # print("in send password reset token")
    # print("user details below")
    # print("type " + str(type(user_source)))
    # print('username' + user_source.username)
    # print(user_source.employee.full_name + ' ' + str(user_source.employee.id))
    # print('email ' + user_source.email)
    token = user_source.get_reset_password_token()
    # with smtplib.SMTP('smtp.gmail.com', 587) as smtp, user as user:
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

    print('text.type ->')
    print(str(type(text)))
    print('html.type ->')
    print(str(type(html)))

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    # pw_email = MIMEText(render_template('email/reset_password.html', user=user_source, token=token), 'html')
    # pw_email['From'] = os.getenv('MAIL_DEFAULT_SENDER')
    # pw_email['To'] = user_source.email
    # pw_email['Subject'] = 'Volstead\'s Vault Password Reset'
    smtp.sendmail(os.getenv('MAIL_DEFAULT_SENDER'), user_source.email, msg.as_string())

    # msg = message.EmailMessage()
    # msg['Subject'] = 'Volstead\'s Vault Password Reset'
    # msg['From'] = os.environ.get('MAIL_USERNAME')
    # msg['To'] = user_source.email
    # print('msg.values() ->')
    # print(msg.values())
    # msg.set_content(render_template('email/reset_password.txt', user=user_source, token=token))
    # print('msg.get_content -> ')
    # print(msg.get_content())
    # #asparagis_cid = make_msgid()
    # msg.add_alternative(render_template('email/reset_password.html', user=user_source, token=token))
    # smtp.send_message(msg)



# def send_password_reset_email(user):
#     token = user.get_reset_password_token()
#     msg = Message()
#     msg.subject = '[Volstead\'s Vault Reset Your Password'
#     msg.recipients = [user.email]
#     msg.body = render_template('email/reset_password.txt', user=user, token=token)
#     msg.html = render_template('email/reset_password.html', user=user, token=token)
#     # with current_app.app_context():
#     print('before mail.send')
#     with mail.connect() as conn:
#         conn.send(msg)
#         print('after mail.send')
#
#     # send_email(subject='[Volstead\'s Vault Reset Your Password',
#     #            sender=Config.ADMINS[0],
#     #            recipients=[user.email],
#     #            text_body=render_template('email/reset_password.txt', user=user, token=token),
#     #            html_body=render_template('email/reset_password.html', user=user, token=token))

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