from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, render_template
from app_setup import verify_authentication


main = Blueprint('main', __name__)


@main.route('/')
def index():
    verify_authentication()
    return render_template('index.html')


@main.route('/todos')
@jwt_required(refresh=True)
def todos():
    verify_authentication()
    user_id = get_jwt_identity()
    user = UserModel.find_by_id(get_jwt_identity())
    todo_list = user.json()['items']
    return render_template('todos.html', todos=todo_list, user_id=user_id)
