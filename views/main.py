import json
from models.item import ItemModel
from flask_jwt_extended import jwt_required
from flask import Blueprint, render_template


main = Blueprint('main', __name__)


def get_app_version():
    try:
        with open("app_version.json", "r") as version_file:
            version_json = json.loads(version_file.read())
            return version_json.get('version', 'unknown')
    except FileNotFoundError:
        return "unknown"


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/todos')
@jwt_required()
def todos():
    todo_list = [item.json() for item in ItemModel.query.all()]
    return render_template('todos.html', todos=todo_list, app_version=get_app_version())
