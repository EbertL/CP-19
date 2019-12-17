from flask import Flask
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{app.instance_path}/app.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    from .db import db, init_app
    init_app(app)
    db.init_app(app)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    from . import auth
    app.register_blueprint(auth.bp)

    from . import view
    app.register_blueprint(view.bp)
    app.add_url_rule('/', endpoint='index')

    # from . import client
    # app.register_blueprint(client.bp)

    return app