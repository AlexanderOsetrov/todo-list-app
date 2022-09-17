from models.user import UserModel
from models.item import ItemModel
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, render_template, redirect, url_for, current_app, flash
from app_setup import verify_authentication


settings = Blueprint('settings', __name__)


@settings.route('/settings')
@jwt_required(refresh=True)
def get_settings():
    verify_authentication()
    user = UserModel.find_by_id(get_jwt_identity())
    if user.name != 'admin':
        return redirect(url_for("main.index"))
    users = [user for user in UserModel.query.all()]
    items = [item for item in ItemModel.query.all()]
    return render_template('settings.html', users=users, items=items)


@settings.route('/settings/user/<user_id>/delete')
@jwt_required(refresh=True)
def delete_user(user_id):
    verify_authentication()
    user = UserModel.find_by_id(user_id)
    if user.name == 'admin':
        flash('Admin user cannot be deleted!')
        return redirect(url_for('settings.get_settings'))
    current_app.logger.info("Removing user: %s" % user.json())
    user.delete_from_db()
    return redirect(url_for("settings.get_settings"))


@settings.route('/settings/item/<item_id>/delete')
@jwt_required(refresh=True)
def delete_item(item_id):
    verify_authentication()
    item = ItemModel.find_by_id(item_id)
    current_app.logger.info("Removing item: %s" % item.json())
    item.delete_from_db()
    return redirect(url_for("settings.get_settings"))
