import os

from flask import Flask, redirect, url_for
from flask_mysqldb import MySQL
from flask_login import LoginManager

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_PORT'] = 3306
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'casper01'
    app.config['MYSQL_DB'] = 'WelcomeHome'
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Initialize database
    from . import db
    db.init_app(app)

    # Register auth blueprint
    from .auth import create_auth_blueprint
    auth_bp = create_auth_blueprint(login_manager)
    app.register_blueprint(auth_bp, url_prefix='/auth')  # Ensure the correct prefix

    # Redirect root URL '/' to login page
    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))

    # A simple page that says hello (optional)
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app