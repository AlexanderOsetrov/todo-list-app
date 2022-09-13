from flask import Flask
from flask_restful import Api
from resources.item import Item, ItemList
from db import db
import os
from flask_login import LoginManager


def get_database_url():
    data_base_url = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
    return data_base_url.replace("postgres", "postgresql")


def create_app():
    flask_app = Flask(__name__, static_url_path='')
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    flask_app.config['SECRET_KEY'] = 'secret'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    api = Api(flask_app)
    api.add_resource(ItemList, '/items', endpoint="items")
    api.add_resource(Item, '/items/<item_id>')

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
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=443)
