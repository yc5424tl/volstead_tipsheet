# coding=utf-8

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from vault import db, vols_email, Config
from vault.auth import bp
from vault.auth.forms import LoginForm, ResetPasswordRequestForm, ResetPasswordForm
from vault.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        # remember = form.remember_me.data
        remember = True # TODO -  FIX THIS GARBAGE CODE
        print('remember = ' + str(remember) + ' type= ' + str(type(remember)))
        user = User.query.filter_by(username=form.username.data).first()
        print(user.username)
        print(user.email)
        print(str(form.password.data))
        if not user or not user.check_password(form.password.data):
            flash('Password/Username Incorrect')
            return redirect(url_for('auth.login', form=LoginForm))
        print('logging in user')
        login_user(user, remember=remember)
        return redirect(url_for('main.start_report'))

    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('main.start_report'))

        form = LoginForm()
        return render_template('login.html', form=form, title=_('Sign In'))


@bp.route('/logout')
def logout():
    logout_user()
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
    # if request.method == 'GET':
    #     form = ResetPasswordRequestForm()
    #     return render_template('reset_password_request.html', form=form)
    #
    # if request.method == 'POST':
    #     form = request.form
    #     if form.validate_on_submit():
    #         user = User.query.filter_by(email=form.email.data).first()
    #         if user:
    #             vols_email.send_password_reset_email(user)
    # flash(_('Check your email for instructions to reset your password'))
    # return redirect(url_for('auth.login'))
        # flash(_('Check your email for instructions to reset your password'))
        # return render_template('reset_password_request.html', title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.start_report'))
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
