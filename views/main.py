from models.item import ItemModel
from app import verify_authentication
from flask_jwt_extended import jwt_required
from flask import Blueprint, render_template


main = Blueprint('main', __name__)


@main.route('/')
def index():
    verify_authentication()
    return render_template('index.html')


@main.route('/todos')
@jwt_required()
def todos():
    todo_list = [item.json() for item in ItemModel.query.all()]
    return render_template('todos.html', todos=todo_list)
