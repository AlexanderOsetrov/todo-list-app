from db import db
from models.user import UserModel
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask import make_response, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, unset_jwt_cookies, jwt_required, verify_jwt_in_request


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = UserModel.find_by_email(email)
    if not user or not check_password_hash(user.password, password):
        flash('Wrong password or email!')
        return redirect(url_for('auth.login'))
    response = make_response(redirect(url_for('main.todos')))
    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(user.id)
    response.set_cookie('access_token_cookie', access_token)
    response.set_cookie('refresh_token_cookie', refresh_token)
    current_app.config['USER_AUTHENTICATED'] = True
    return response


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    user = UserModel.find_by_email(email)
    if user:
        flash('Email address already exists!')
        return redirect(url_for('auth.signup'))
    new_user = UserModel(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@jwt_required()
def logout():
    response = make_response(redirect(url_for('main.index')))
    unset_jwt_cookies(response)
    current_app.config['USER_AUTHENTICATED'] = False
    return response
