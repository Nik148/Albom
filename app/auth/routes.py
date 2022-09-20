from flask import render_template, url_for, redirect, flash, get_flashed_messages, request, current_app
from flask_login import current_user, login_user, logout_user
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordForm, NewPasswordForm
from app.auth.email import send_confirmation_registration, send_password_reset
from app.models import User
from werkzeug.urls import url_parse
from app import db
from flask_babel import _

@bp.route("/login", methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template("auth/login.html", form=form)

@bp.route("/register", methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        token = User.get_new_user_token(username=form.username.data, email=form.email.data, password=form.password.data)
        send_confirmation_registration(token=token, email=form.email.data)
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)

@bp.route("/save_new_user/<token>")
def save_new_user(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    token_decode = User.verify_new_user_token(token)
    if token_decode:
        user = User(username=token_decode['username'], email=token_decode['email'])
        user.set_password(token_decode['password'])
        db.session.add(user)
        db.session.commit()
    return redirect(url_for('auth.login'))  

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@bp.route("/reset_password", methods=('GET', 'POST'))
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)        

@bp.route('/new_password/<token>', methods=['GET', 'POST'])
def new_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = NewPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/new_password.html', form=form)