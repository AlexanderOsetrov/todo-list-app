from models.user import UserModel
from models.item import ItemModel
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, render_template, redirect, url_for
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


@main.route('/settings')
@jwt_required(refresh=True)
def settings():
    verify_authentication()
    user = UserModel.find_by_id(get_jwt_identity())
    if user.name != 'admin':
        return redirect(url_for("main.index"))
    users = [user for user in UserModel.query.all()]
    items = [item for item in ItemModel.query.all()]
    return render_template('settings.html', users=users, items=items)


# @main.route('/settings/user/<user_id>/delete')
# @jwt_required(refresh=True)
# def delete_user(user_id):
#     verify_authentication()
#     user = UserModel.find_by_id(user_id)
#     user.delete_from_db()
#     return redirect(url_for("settings"))
