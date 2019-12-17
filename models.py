from .db import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    valid = db.Column(db.Boolean, nullable=False, default=0)
    admin = db.Column(db.Boolean, nullable=False, default=0)

    def __repr__(self):
        return f"<User {self.id} - {self.name}>"

    def __getitem__(self, item):
        return getattr(self, item)


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<Item {self.id} - {self.name}>"

    def __getitem__(self, item):
        return getattr(self, item)


class Record(db.Model):
    __tablename__ = "records"
    id = db.Column(db.Integer, primary_key=True)
    operation_time = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    operation = db.Column(db.Enum("TOOK", "ADDED"))
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Record {self.id}>"

    def __getitem__(self, item):
        return getattr(self, item)
