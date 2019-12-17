from flask import (
    Blueprint, redirect, render_template, request, url_for, flash, g
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
    return render_template('view/index.html', names=names)


@bp.route('/database/<tname>')
@login_required
def viewer(tname):
    cur = db.session.execute(f"SELECT * FROM {tname}")
    if tname == "records":
        cur = db.session.execute(f"SELECT * FROM records_view")
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
                flash("Data inserted", "success")
            else:
                abort(500)
        except StatementError:
            flash("Got wrong value. Please write for Boolean 1/0 or True/False.", "error")

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

        if "valid" in k.keys() and k['valid'].lower() in boolean.keys():
            k["valid"] = boolean[k['valid'].lower()]
        if "admin" in k.keys() and k['admin'] in boolean.keys():
            k["admin"] = boolean[k['admin'].lower()]

        try:
            if tname in tables.keys():
                new = tables[tname].query.get(id)
                for key, value in k.items():
                    setattr(new, key, value)
                    db.session.commit()
                flash("Data changed", "success")
            else:
                abort(500)
        except StatementError as e:
            flash("Got wrong value. Please write for Boolean 1/0 or True/False.", "error")

        return redirect(url_for('view.viewer', tname=tname))

    return render_template('view/edit.html', names=names, col_names=col_names, tname=tname, results=result)


@bp.route("/client", methods=('GET', 'POST'))
def form_client():
    items = Item.query.all()
    if request.method == "POST":
        k = request.form.to_dict()
        error = None
        if k["option"] == 'addOption':
            if k['itemControl'] == 'addNew' and k['newItem'] != "":
                new = Item(name=k["newItem"], quantity=k['quantityField'])
                db.session.add(new)
                db.session.commit()
                obj = Item.query.filter_by(name=new.name).first()
                new_rec = Record(user_id=g.user.id, operation="ADDED", item_id=obj.id, quantity=k["quantityField"])
                db.session.add(new_rec)
                db.session.commit()
                flash(f"{new.name} added!", "success")
                return render_template('view/index.html', names=names)
            elif k['itemControl'] in [str(i[0]) for i in db.session.query(Item.id).all()]:
                obj = Item.query.get(int(k['itemControl']))
                obj.quantity = int(obj.quantity) + int(k['quantityField'])
                new_rec = Record(user_id=g.user.id, operation="ADDED", item_id=obj.id, quantity=k["quantityField"])
                db.session.add(new_rec)
                db.session.commit()
                flash(f"Successfully added {k['quantityField']} to {obj.name}!", "success")
                return render_template('view/index.html', names=names)
            else:
                error = "Problems with entered data."
        elif k["option"] == "takeOption":
            obj = Item.query.get(int(k['itemControl']))
            if int(k["quantityField"]) <= int(obj.quantity):
                obj.quantity = int(obj.quantity) - int(k['quantityField'])
                new_rec = Record(user_id=g.user.id, operation="TOOK", item_id=obj.id, quantity=k["quantityField"])
                db.session.add(new_rec)
                db.session.commit()
                flash(f"Successfully took  {k['quantityField']} from {obj.name}!", "success")
                return render_template('view/index.html', names=names)
            else:
                error = f"You trying to take {k['quantityField']} from {obj.name} but there is only {obj.quantity}!"
        else:
            error = "Troubles occurred."

        if error is None:
            return render_template('view/index.html', names=names)

        flash(error, "error")
    return render_template("view/client_form.html", items=items, names=names)
