import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, copy_current_request_context
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import db
from . import models
from sqlalchemy.exc import IntegrityError

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        error = None
        # admin = db.execute('SELECT * FROM admins WHERE phone=?', (phone,)).fetchone()
        print(models.User.query.first().__dict__)
        user = models.User.query.filter_by(phone=phone).first()
        print(user)

        if user is None:
            error = 'Incorrect phone number.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'
        elif user.valid == 0:
            error = "Account not valid yet."

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error, "error")
    # db.session.add(models.User(phone="1111", name='1', password=generate_password_hash('1'), admin=1, valid=1))
    # db.session.commit()
    return render_template('auth/login.html')


@bp.route('/register', methods=("GET","POST"))
def register():
    if request.method == "POST":
        phone = request.form['phone']
        password = request.form['password']
        name = request.form["name"]
        error = None

        if len(phone) < 5:
            error = "Short password. Minimum 5 characters required!"

        try:
            if error is None:
                user = models.User(name=name, phone=phone, password=generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
                flash("Registered", "success")
                return redirect(url_for('auth.login'))
        except IntegrityError:
            flash("User already exists.", "error")

    return render_template("auth/register.html")


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            models.User.query.get(user_id)
        )
