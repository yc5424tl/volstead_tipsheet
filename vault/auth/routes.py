# coding=utf-8

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from flask_babel import _
from werkzeug.urls import url_parse

from vault import db, vols_email, login as login_mgr
from vault.auth import bp
from vault.auth.forms import LoginForm, ResetPasswordRequestForm, ResetPasswordForm, RegistrationForm
from vault.models import User

import logging
import sys

root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


@login_mgr.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.start_report'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()


        if user and user.check_password(form.password.data):
            user.active = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.start_report'))

        if ( user is None ) or ( not user.check_password(form.password.data) ):
            flash('Invalid username and/or password')
            return redirect(url_for('auth.login'))

        login_mgr.login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.start_report')

        flash('Login Successful')
        return redirect(next_page)

    flash('There was an error processing your submission, please try again.')
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
@login_required
def logout():
    user = current_user
    user.active = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash('Sign Out Successful')
    return redirect(url_for('auth.login'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            vols_email.send_password_reset_email(user)
        flash(_('Check your email for instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html', title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
# @roles_required('Admin')
@login_required
def register():
    for role in current_user.roles:
        if role.name == 'Admin':
            form = RegistrationForm()
            if form.validate_on_submit():
                user = User(username=form.username.data, email=form.email.data)
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                flash(user.username + ' successfully registered.')
                return redirect(url_for('auth.login'))
            flash('Invalid Form Submission, Please Try Again')
            return render_template('register.html', title='Register New User', form=form)
    flash('Insufficient Authorization')
    return redirect(url_for('auth.login'))
