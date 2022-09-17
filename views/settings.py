from db import db
from models.user import UserModel
from models.item import ItemModel
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, render_template, redirect, url_for, current_app, flash, request
from app_setup import verify_authentication
from werkzeug.security import generate_password_hash


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


@settings.route('/settings/user/<user_id>')
@jwt_required(refresh=True)
def edit_user(user_id):
    verify_authentication()
    user = UserModel.find_by_id(user_id)
    return render_template('user.html', email=user.email, name=user.name, user_id=user.id)


@settings.route('/settings/user/<user_id>/edit', methods=['POST'])
@jwt_required(refresh=True)
def update_user(user_id):
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    user = UserModel.find_by_email(email)
    if user and int(user_id) != int(user.id):
        flash('Email address already exists!')
        return redirect(url_for('settings.edit_user', user_id=user_id))
    edited_user = UserModel.find_by_id(user_id)
    edited_user.name = name
    edited_user.email = email
    if password != "":
        edited_user.password = generate_password_hash(password)
    edited_user.save_to_db()
    return redirect(url_for("settings.get_settings"))


@settings.route('/settings/item/<item_id>')
@jwt_required(refresh=True)
def edit_item(item_id):
    verify_authentication()
    item = ItemModel.find_by_id(item_id)
    return render_template('item.html', item_id=item.item_id, title=item.title)


@settings.route('/settings/item/<item_id>/edit', methods=['POST'])
@jwt_required(refresh=True)
def update_item(item_id):
    title = request.form.get('title')
    edited_item = ItemModel.find_by_id(item_id)
    if edited_item.title != title:
        edited_item.title = title
        edited_item.save_to_db()
    return redirect(url_for("settings.get_settings"))
