from flask import Flask, render_template
from flask_restful import Api
from resources.item import Item, ItemList
from db import db
import os
import json


def get_database_url():
    data_base_url = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
    return data_base_url.replace("postgres", "postgresql")


def get_app_version():
    try:
        with open("app_version.json", "r") as version_file:
            version_json = json.loads(version_file.read())
            return version_json.get('version', 'unknown')
    except FileNotFoundError:
        return "unknown"


def create_app():
    flask_app = Flask(__name__, static_url_path='')
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    api = Api(flask_app)
    api.add_resource(ItemList, '/items', endpoint="items")
    api.add_resource(Item, '/items/<item_id>')

    from auth import auth as auth_blueprint
    flask_app.register_blueprint(auth_blueprint)

    from main import main as main_blueprint
    flask_app.register_blueprint(main_blueprint)

    @flask_app.before_first_request
    def create_tables():
        db.create_all()

    # @flask_app.route('/')
    # def index():
    #     todos = ItemList().get()
    #     app_version = get_app_version()
    #     return render_template('todos.html', todos=todos, app_version=app_version)
    return flask_app


def init_db(flask_app):
    db.init_app(flask_app)


app = create_app()
init_db(app)


if __name__ == '__main__':
    app.run(debug=True, port=443)
