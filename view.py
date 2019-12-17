from flask import (
    Blueprint, redirect, render_template, request, url_for, flash
)

from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash
from .auth import login_required
from .db import db
from .models import User, Item, Record
from sqlalchemy.exc import StatementError

bp = Blueprint('view', __name__)

tables = {"users": User,
          "items": Item,
          "records": Record}

boolean = {"true": 1, "1": 1, "false": 0, "0": 0}
names = db.metadata.tables.keys()


@bp.route('/')
@login_required
def index():
    print(names)
    return render_template('view/index.html', names=names)


@bp.route('/database/<tname>')
@login_required
def viewer(tname):
    cur = db.session.execute(f"SELECT * FROM {tname}")
    results = [{column: value for column, value in row.items()} for row in cur]
    col_names = [elem for elem in cur.keys()]
    return render_template('view/view.html', tname=tname, col_names=col_names, results=results, names=names)


@bp.route("/database/<tname>/insert", methods=['POST', "GET"])
@login_required
def inserter(tname):
    cur = db.session.execute(f"SELECT * FROM {tname}")
    # results = [{column: value for column, value in row.items()} for row in cur]
    col_names = [elem for elem in cur.keys()]

    if request.method == 'POST':
        k = request.form.to_dict()
        if 'password' in k.keys() and k['password'] != '':
            k['password'] = generate_password_hash(k['password'])
        if "valid" in k.keys() and k['valid'] in boolean.keys():
            k["valid"] = boolean[k['valid'].lower()]
        if "admin" in k.keys() and k['admin'] in boolean.keys():
            k["admin"] = boolean[k['admin'].lower()]

        if "operation" in k.keys():
            k["operation"] = k["operation"].upper()

        try:
            if tname in tables.keys():
                new = tables[tname](**k)
                db.session.add(new)
                db.session.commit()
            else:
                abort(500)
        except StatementError:
            flash("Got wrong value. Please write for Boolean 1/0 or True/False.")

        return redirect(url_for('view.viewer', tname=tname))

    return render_template('view/insert.html', names=names, col_names=col_names, tname=tname)


@bp.route("/database/<tname>/edit/<id>", methods=('GET', 'POST'))
@login_required
def editor(tname, id):
    cur = db.session.execute(f"SELECT * FROM {tname}")
    col_names = [elem for elem in cur.keys()]
    result = None
    if tname in tables.keys():
        result = tables[tname].query.get(id)
    else:
        abort(500)

    if request.method == 'POST':
        k = request.form.to_dict()
        if 'password' in k.keys() and k['password'] != '':
            k['password'] = generate_password_hash(k['password'])
        elif 'password' in k.keys():
            k.pop('password')

        if "valid" in k.keys() and k['valid'] in boolean.keys():
            k["valid"] = boolean[k['valid'].lower()]
        if "admin" in k.keys() and k['admin'] in boolean.keys():
            k["admin"] = boolean[k['admin'].lower()]

        try:
            if tname in tables.keys():
                new = tables[tname].query.get(id)
                for key, value in k.items():
                    setattr(new, key, value)
                    db.session.commit()
            else:
                abort(500)
        except StatementError:
            flash("Got wrong value. Please write for Boolean 1/0 or True/False.")

        return redirect(url_for('view.viewer', tname=tname))

    return render_template('view/edit.html', names=names, col_names=col_names, tname=tname, results=result)


@bp.route("/client", methods=('GET', 'POST'))
def form_client():
    items = Item.query.all()
    if request.method == "POST":
        k = request.form.to_dict()
        error = None
        print(k)
        if k["option"] == 'addOption':
            pass



    return render_template("view/client_form.html", items=items)
