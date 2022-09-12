from flask import Blueprint, render_template
from db import db
from resources.item import ItemList


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/todos')
def todos():
    todo_list = ItemList().get()
    # app_version = get_app_version()
    return render_template('todos.html', todos=todo_list, app_version="1.0")

