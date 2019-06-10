# coding=utf-8

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_user import roles_required
from flask_babel import _
from werkzeug.urls import url_parse

from vault import db, vols_email, Config
from vault.auth import bp
from vault.auth.forms import LoginForm, ResetPasswordRequestForm, ResetPasswordForm, RegistrationForm
from vault.models import User, Employee, Role
from vol_app import app




# @bp.route('/login', methods=['GET', 'POST'])
#
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.start_report'))
#     login_form = LoginForm(request.form)
#     if request.method == 'POST':
#         # remember = form.remember_me.data
#         remember = True # TODO -  FIX THIS GARBAGE CODE
#         print('remember = ' + str(remember) + ' type= ' + str(type(remember)))
#
#         users = User.query.all()
#         if users is None:
#             print("Empty User Table")
#         else:
#             for user in users:
#                 print(user.username)
#
#         user = User.query.filter_by(username=login_form.username.data).first()
#         if user:
#             print(user.username)
#             print(user.email)
#             print(str(login_form.password.data))
#         if not user or not user.check_password(login_form.password.data):
#             print('Password/Username Incorrect')
#             return redirect(url_for('auth.login', form=LoginForm))
#         print('logging in user')
#         login_user(user, remember=remember)
#         return redirect(url_for('main.start_report'))
#
#     if request.method == 'GET':
#         # if current_user.is_authenticated:
#         #     return redirect(url_for('main.start_report'))
#
#         signin_form = LoginForm()
#         return render_template('login.html', form=signin_form, title=_('Sign In'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.start_report'))
    form = LoginForm()
    if form.validate_on_submit():
        app.logger('in form.validate_on_submit() in auth.routes')
        user = User.query.filter_by(username=form.username.data).first()
        app.logger('=======================')
        app.logger('form.username.data ->')
        app.logger(form.username.data)
        app.logger('======================')
        app.logger('user ->')
        app.logger(user)
        app.logger('=======================')
        app.logger('form.password.data ->')
        app.logger(form.password.data)
        app.logger('=======================')
        app.logger('request.form.get("password") ->')
        app.logger(request.form.get('password'))
        app.logger('=======================')
        app.logger('request.form.get("username") ->')
        app.logger(request.form.get('username'))
        app.logger('========================')
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username and/or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.start_report')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

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

@bp.route('/register', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(user.username + ' successfully registered.')
        return redirect(url_for('admin_panel'))
    return render_template('register.html', title='Register New User', form=form)

# @login.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
# @login.unauthorized_handler
# def unauthorized():
#     flash('Restricted Access: Login/Authorization')
#     return redirect(url_for('auth.login'))