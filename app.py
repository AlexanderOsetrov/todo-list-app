from db import db
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from app_setup import set_app_config, register_api_resources, create_default_admin


def create_app():
    flask_app = Flask(__name__, static_url_path='', static_folder='static')
    set_app_config(flask_app)
    api = Api(flask_app)
    register_api_resources(api)
    jwt = JWTManager(flask_app)
    from views.auth import auth as auth_blueprint
    from views.main import main as main_blueprint
    from views.settings import settings as settings_blueprint
    flask_app.register_blueprint(auth_blueprint)
    flask_app.register_blueprint(main_blueprint)
    flask_app.register_blueprint(settings_blueprint)
    db.init_app(flask_app)
    return flask_app


app = create_app()
db.create_all(app=app)
create_default_admin(app)

if __name__ == '__main__':
    app.run(debug=True, port=443)
