# coding=utf-8

from flask import render_template, current_app
from flask_babel import _
from vault import LoginManager

from vault.vols_email import send_email


# def send_password_reset_email():
#     user = cuee
#     token = current_user.get_reset_password_token()
#     send_email(_('[Volstead\'s Vault Reset Your Password'),
#                sender=current_app.config['ADMINS'][0],
#                recipients=[current_user.email],
#                text_body=render_template('email/reset_password.txt', user=current_user, token=token),
#                html_body=render_template('email/reset_password.html', user=current_user, token=token))