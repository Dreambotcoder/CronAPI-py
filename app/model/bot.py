from app import db
from app.model.rooms import Room


class Bot(db.Model):
    __tablename__= "bots"
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey(Room.id))
    ingame_name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    data = db.Column(db.String(5000))
    clock_in = db.Column(db.DateTime, nullable=False)
    clock_out = db.Column(db.DateTime)
    active = db.Column(db.Boolean, nullable=False)
    script_id = db.Column(db.Integer, db.ForeignKey("scripts.id"))

    room = db.relationship(Room, foreign_keys=room_id, backref="bots")
    script = db.relationship("Script", foreign_keys=script_id, backref = "bots")

    @staticmethod
    def get_bots():
        return db.session.query(Bot)


class Script(db.Model):
    __tablename__= "scripts"
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    script_name = db.Column(db.String(100), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)

    @staticmethod
    def get_scripts():
        return db.session.query(Script)