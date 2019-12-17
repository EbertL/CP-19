from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
import click
from flask.cli import with_appcontext


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        # DATABASE=os.path.join(app.instance_path, "app.db"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{app.instance_path}/app.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    from .db import db
    db.init_app(app)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        app.cli.add_command(init_db_command)

    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    from . import auth
    app.register_blueprint(auth.bp)

    from . import view
    app.register_blueprint(view.bp)
    app.add_url_rule('/', endpoint='index')
    #
    # from . import client
    # app.register_blueprint(client.bp)

    # @app.route("/")
    # def index():
    #     from .models import Item, User
    #     # item1 = Item(name="Pen212")
    #     # db.session.add(item1)
    #     # db.session.add(User(name="admin", password='1234qwer', phone="0965657867", valid=1, admin=1))
    #     # db.session.commit()
    #     print(Item.query.all(), User.query.all())
    #     print(db.metadata.tables.keys())
    #     print(User.__table__.c.keys())
    #     print(User.query.first()['name'])
    #     return "Hello"

    return app


def init_db():
    from .models import User, Record, Item
    from .db import db
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Initialized the database.")

#
# if __name__ == '__main__':
#     create_app().run()