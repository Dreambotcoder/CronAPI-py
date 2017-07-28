from app import db


class Room(db.Model):
    __tablename__= "rooms"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    token = db.Column(db.String(100), nullable=False)
    token_pass = db.Column(db.String(100),nullable=False)


    @staticmethod
    def get_rooms():
        return db.session.query(Room)
