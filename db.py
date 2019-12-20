import click
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


def init_db():
    from .models import User, Record, Item
    db.drop_all()
    db.create_all()
    db.session.execute("""DROP VIEW IF EXISTS records_view;""")
    db.session.execute("""
    CREATE VIEW records_view AS SELECT records.id, records.operation_time, users.name AS user_name, records.operation, items.name AS item_name,
     records.quantity FROM records INNER JOIN users ON records.user_id=users.id INNER JOIN items ON records.item_id=items.id;
    """)
    admin = User(name="admin", phone="0965657867", password=generate_password_hash("1234qwer"), valid=1, admin=1)
    db.session.add(admin)
    db.session.commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.cli.add_command(init_db_command)
