from db import db


class ItemModel(db.Model):

    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    completed = db.Column(db.Boolean)
    order = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, title, completed, order, user_id):
        self.title = title
        self.completed = completed
        self.order = order
        self.user_id = user_id

    def json(self):
        return {'id': self.item_id, 'title': self.title, 'completed': self.completed,
                'order': self.order, 'user_id': self.user_id}

    @classmethod
    def find_by_id(cls, item_id):
        return cls.query.filter_by(item_id=item_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_all(cls):
        db.session.query(ItemModel).delete()
        db.session.commit()
