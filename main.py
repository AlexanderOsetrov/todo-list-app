from flask import Blueprint, render_template
import json
from resources.item import ItemList
from flask_login import login_required, current_user


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
@login_required
def todos():
    todo_list = ItemList().get()
    return render_template('todos.html', todos=todo_list, app_version=get_app_version())
