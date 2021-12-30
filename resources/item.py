from flask_restful import Resource, reqparse
from models.item import ItemModel


class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'title', type=str, required=True, help="Parameter 'title' is not provoded"
    )
    parser.add_argument(
        'completed', type=bool, required=True, help="Parameter 'completed' is not provoded"
    )
    parser.add_argument(
        'order', type=int, required=True, help="Parameter 'order' is not provoded"
    )

    def get(self, item_id):
        item = ItemModel.find_by_id(item_id)
        if item:
            
            return item.json()
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404        

    def delete(self, item_id):
        item = ItemModel.find_by_id(item_id)
        if item:
            item.delete_from_db()
            return {'message': f"Item '{item_id}' is deleted"}, 204
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404

    def put(self, item_id):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_id(item_id)
        item.title = data['title']
        item.completed = data['completed']
        item.save_to_db()
        return item.json()


class ItemList(Resource):

    def get(self):
        return [item.json() for item in ItemModel.query.all()]

    def post(self):
        data = Item.parser.parse_args()
        item = ItemModel(**data)
        try:
            item.save_to_db()
        except Exception:
            return {'message': "An error occured inserting the item"}, 500
        return item.json(), 201

    def delete(self):
        ItemModel.delete_all()
        return [item.json() for item in ItemModel.query.all()]
