# # coding=utf-8
#
# from flask import url_for, redirect, flash, render_template, request
# from flask_babel import _
# from flask_login import login_required, current_user, login_user, logout_user
# from flask_user import roles_required
#
# from app import app
#
# from auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, EditProfileForm
# from volsteads.email import send_password_reset_email
# from volsteads.models import User
# from werkzeug.urls import url_parse
# from volsteads import mongo
#
#
# @app.route('/')
# @app.route('/index')
# @login_required
# def index():
#     return render_template("index.html", title="Volstead's Vault")
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('report_form'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         invoking_user = User.query.filter_by(username=form.username.data).first()
#         if invoking_user is None or not invoking_user.check_password(form.password.data):
#             flash('Invalid username and/or password.')
#             return redirect(url_for('login'))
#         login_user(invoking_user, remember=form.remember_me.data)
#         # next_page = request.args.get('next')
#         # if not next_page or url_parse(next_page).netloc != '':
#         #     next_page = url_for('index')
#         #     return redirect(next_page)
#         return redirect(url_for('report_form'))
#     return render_template('login.html', title='Sign In', form=form)
#
#
#
#
#
# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for())
#
#
#
# @app.route('/admin/register', methods=['GET', 'POST'])
# @login_required
# @roles_required('Admin')
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('build_report'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         invoking_user = User(username=form.username.data, email=form.email.data)
#         invoking_user.set_password(form.password.data)
#         mongo.db.session.add(invoking_user)
#         mongo.db.session.commit()
#         flash('New User Created Successfully.')
#         return redirect(url_for('login'))
#     return render_template('register.html', title="Register", form=form)
#
#
# @app.route('/reset_password_request', methods=['GET', 'POST'])
# def reset_password_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = ResetPasswordRequestForm()
#     if form.validate_on_submit():
#         invoking_user = User.query.filter_by(email=form.email.data).first()
#         if invoking_user:
#             send_password_reset_email(invoking_user)
#         flash('An email containing a link to reset your password has been sent.')
#         return redirect(url_for('login'))
#     return render_template('reset_password_request.html', title='Reset Password', form=form)
#
#
# @app.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     invoking_user = User.verify_reset_password_token(token)
#     if not invoking_user:
#         return redirect(url_for('index'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         invoking_user.set_password(form.password.data)
#         mongo.db.session.commit()
#         flash('Your password has been reset.')
#         return redirect(url_for('login'))
#     return render_template('reset_password.html', form=form)
#
#
# # @bp.route('/user/<username>')   KEEP FOR LATER
# @app.route('/user/<username>')
# @login_required
# def user(username):
#     active_user = User.query.filter_by(username=username).first_or_404()
#     return render_template('user.html', user=active_user)
#
#
#
# # @bp.route('/edit_profile', methods=['GET', 'POST'])    KEEP FOR LATER
# @app.route('/edit_profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#     form = EditProfileForm(current_user.username)
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         current_user.about_me = form.about_me.data
#         mongo.db.session.commit()
#         flash(_('Your changes have been saved.'))
#         return redirect(url_for('main.edit_profile'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', title=_('Edit Profile'), form=form)
