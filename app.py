import os
from db import db
from flask import Flask
from flask_restful import Api
from models.user import UserModel
from flask_login import LoginManager
from logging.config import dictConfig
from flask_jwt_extended import JWTManager
from resources.item import Item, ItemList
from resources.user import UserRegister, UserLogin


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


def get_database_url():
    data_base_url = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
    return data_base_url.replace("postgres", "postgresql")


def create_app():
    flask_app = Flask(__name__, static_url_path='')
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    flask_app.config['SECRET_KEY'] = 'secret'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    api = Api(flask_app)

    jwt = JWTManager(flask_app)
    api.add_resource(ItemList, '/api/items', endpoint="items")
    api.add_resource(Item, '/api/items/<item_id>')
    api.add_resource(UserRegister, '/api/register')
    api.add_resource(UserLogin, '/api/login')

    from views.auth import auth as auth_blueprint
    flask_app.register_blueprint(auth_blueprint)

    from views.main import main as main_blueprint
    flask_app.register_blueprint(main_blueprint)

    @flask_app.before_first_request
    def create_tables():
        db.create_all()

    db.init_app(flask_app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(flask_app)

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.query.get(int(user_id))

    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=443)
