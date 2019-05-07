# coding=utf-8

from flask import render_template, current_app
from flask_babel import _
import email

# from volsteads import app
# from flask import render_template
#
# def send_password_reset_emal(user):
#     token = user.get_reset_password_token()
#     send_email('[Volstead\'s Vault Reset Your Password')

#
               #text_body=render_template('email/reset_password.txt', user=user, token=token),
               #html_body=render_template('email/reset_password.html', user=user, token=token))