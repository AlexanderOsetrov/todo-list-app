import os
import json
from db import db
from datetime import timedelta
from flask import Flask, current_app
from flask_restful import Api
from logging.config import dictConfig
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from resources.item import Item, ItemList, UserItem
from resources.user import UserRegister, UserLogin
from models.user import UserModel
from werkzeug.security import generate_password_hash


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s\t[%(name)s.%(funcName)s:%(lineno)d.%(levelname)s]\t%(message)s',
        'datefmt': '%b %d %H:%M:%S'
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'}
            },
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})


def get_app_version():
    try:
        with open("app_version.json", "r") as version_file:
            version_json = json.loads(version_file.read())
            return version_json.get('version', 'unknown')
    except FileNotFoundError:
        return "unknown"


def get_database_url():
    data_base_url = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
    return data_base_url.replace("postgres", "postgresql")


def verify_authentication():
    token = verify_jwt_in_request(optional=True, refresh=True)
    if token is None:
        current_app.logger.debug(f"JWT Token is missing.")
        current_app.config['USER_AUTHENTICATED'] = False
    else:
        current_app.logger.debug("JWT Token found: %s" % token[-1])
        current_app.config['USER_AUTHENTICATED'] = True
        current_app.config['CURRENT_USER'] = token[-1].get("user", 'guest')


def set_app_config(flask_app):
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    flask_app.config['SECRET_KEY'] = 'secret'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    flask_app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    flask_app.config['CURRENT_USER'] = 'guest'
    flask_app.config['USER_AUTHENTICATED'] = False
    flask_app.config['APP_VERSION'] = f"Ver. {get_app_version()}"
    flask_app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)


def register_api_resources(api):
    api.add_resource(ItemList, '/api/items', endpoint="items")
    api.add_resource(Item, '/api/items/<item_id>')
    api.add_resource(UserRegister, '/api/register')
    api.add_resource(UserLogin, '/api/login')
    api.add_resource(UserItem, '/api/user/<user_id>/items', endpoint="user_items")
    api.add_resource(UserItem, '/api/user/<user_id>/items/<item_id>')


def create_default_admin(flask_app):
    with flask_app.app_context():
        user = UserModel.find_by_name("admin")
        if user is None:
            user = UserModel(email="admin@admin.com",
                             name="admin",
                             password=generate_password_hash("admin", method='sha256'))
            user.save_to_db()


def create_app():
    flask_app = Flask(__name__, static_url_path='')
    set_app_config(flask_app)
    api = Api(flask_app)
    register_api_resources(api)
    jwt = JWTManager(flask_app)
    from views.auth import auth as auth_blueprint
    from views.main import main as main_blueprint
    flask_app.register_blueprint(auth_blueprint)
    flask_app.register_blueprint(main_blueprint)
    db.init_app(flask_app)
    return flask_app


if __name__ == '__main__':
    app = create_app()
    db.create_all(app=app)
    create_default_admin(app)
    app.run(debug=True, port=443)
