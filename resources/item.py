from models.item import ItemModel
from models.user import UserModel
from flask import current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse


class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'title', type=str, required=True, help="Parameter 'title' is not provided"
    )
    parser.add_argument(
        'completed', type=bool, required=True, help="Parameter 'completed' is not provided"
    )
    parser.add_argument(
        'order', type=int, required=True, help="Parameter 'order' is not provided"
    )

    @jwt_required()
    def get(self, item_id: int):
        item = ItemModel.find_by_id(item_id)
        if item:
            app.logger.info("Got the item from DB: %s" % item.json())
            return item.json()
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404

    @jwt_required()
    def delete(self, item_id: int):
        item = ItemModel.find_by_id(item_id)
        if item:
            app.logger.info("Deleting the item from DB: %s" % item.json())
            item.delete_from_db()
            return {'message': f"Item '{item_id}' is deleted"}, 204
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404

    @jwt_required()
    def put(self, item_id: int):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_id(item_id)
        app.logger.info("Got the item from DB: %s" % item.json())
        item.title = data['title']
        item.completed = data['completed']
        app.logger.info("Updating the item: %s" % item.json())
        item.save_to_db()
        return item.json()


class ItemList(Resource):

    @jwt_required()
    def get(self):
        items = [item.json() for item in ItemModel.query.all()]
        app.logger.info("Got items from DB: %s" % items)
        return items

    @jwt_required()
    def post(self):
        data = Item.parser.parse_args()
        data['user_id'] = get_jwt_identity()
        app.logger.info("Got request data from UI: %s" % data)
        item = ItemModel(**data)
        try:
            app.logger.info("Adding the item to DB: %s" % item.json())
            item.save_to_db()
        except Exception as e:
            app.logger.debug("An exception occurred: %s" % e)
            return {'message': "An error occurred inserting the item"}, 500
        return item.json(), 201

    @jwt_required()
    def delete(self):
        ItemModel.delete_all()
        return [item.json() for item in ItemModel.query.all()]


class UserItem(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'title', type=str, required=True, help="Parameter 'title' is not provided"
    )
    parser.add_argument(
        'completed', type=bool, required=True, help="Parameter 'completed' is not provided"
    )
    parser.add_argument(
        'order', type=int, required=True, help="Parameter 'order' is not provided"
    )

    @jwt_required()
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        todos = user.json()['items']
        app.logger.info("Got items from DB for user '%s': %s" % (user.json().get("name"), todos))
        return todos

    @jwt_required()
    def delete(self, user_id: int, item_id: int):
        if int(user_id) == get_jwt_identity():
            item = ItemModel.find_by_id(item_id)
            if item:
                app.logger.info("Deleting the item from DB: %s" % item.json())
                item.delete_from_db()
                return {'message': f"Item '{item_id}' is deleted"}, 204
            else:
                return {'message': f"Item '{item_id}' is not found"}, 404
        else:
            return {'message': "You're not allowed to delete this item"}, 403

    @jwt_required()
    def post(self, user_id):
        data = UserItem.parser.parse_args()
        data['user_id'] = user_id
        app.logger.info("Got request data from UI: %s" % data)
        item = ItemModel(**data)
        try:
            app.logger.info("Adding the item to DB: %s" % item.json())
            item.save_to_db()
        except Exception as e:
            app.logger.debug("An exception occurred: %s" % e)
            return {'message': "An error occurred inserting the item"}, 500
        return item.json(), 201

    @jwt_required()
    def put(self, user_id: int, item_id: int):
        if int(user_id) == get_jwt_identity():
            data = UserItem.parser.parse_args()
            item = ItemModel.find_by_id(item_id)
            app.logger.info("Got the item from DB: %s" % item.json())
            item.title = data['title']
            item.completed = data['completed']
            app.logger.info("Updating the item: %s" % item.json())
            item.save_to_db()
            return item.json()
        else:
            return {'message': "You're not allowed to update this item"}, 403
