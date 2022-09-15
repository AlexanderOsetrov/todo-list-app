from flask_restful import Resource, reqparse
from models.user import UserModel
from flask import current_app as app
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required)
from werkzeug.security import generate_password_hash, check_password_hash


class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'email', type=str, required=True, help="Parameter 'email' is not provided"
    )
    parser.add_argument(
        'name', type=str, required=True, help="Parameter 'name' is not provided"
    )
    parser.add_argument(
        'password', type=str, required=True, help="Parameter 'password' is not provided"
    )

    def post(self):
        data = UserRegister.parser.parse_args()
        app.logger.info("Got request data: %s" % data)
        if UserModel.find_by_email(data['email']):
            return {"message": "User with this email is already exists"}, 400
        data['password'] = generate_password_hash(data['password'], method='sha256')
        user = UserModel(**data)
        try:
            app.logger.info("Adding the user to DB: %s" % data)
            user.save_to_db()
            app.logger.debug("Added the user to DB: %s" % UserModel.find_by_email(data['email']).json())
        except Exception as e:
            app.logger.debug("An exception occurred: %s" % e)
            return {'message': "An error occurred inserting the item"}, 500
        return user.json(), 201


class User(Resource):

    @jwt_required()
    def get(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        return user.json(), 200

    @jwt_required()
    def delete(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200


class UserLogin(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'email', type=str, required=True, help="Parameter 'email' is not provided"
    )
    parser.add_argument(
        'password', type=str, required=True, help="Parameter 'password' is not provided"
    )

    def post(self):
        data = UserLogin.parser.parse_args()
        user = UserModel.find_by_email(data['email'])
        if not user or not check_password_hash(user.password, data['password']):
            return {'message': 'Invalid credentials'}, 401
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        headers = [('Set-Cookie', f'access_token_cookie={access_token}'),
                   ('Set-Cookie', f'refresh_token_cookie={refresh_token}')]
        return {'login': True}, 200, headers
