from sqlalchemy import desc

from app import db


class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    token = db.Column(db.String(100), nullable=False)
    token_pass = db.Column(db.String(100), nullable=False)
    script_id = db.Column(db.Integer, db.ForeignKey("scripts.id"))

    script = db.relationship("Script", foreign_keys=script_id, backref="rooms")

    @staticmethod
    def get_rooms():
        return db.session.query(Room)


class Bot(db.Model):
    __tablename__ = "bots"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey(Room.id))
    ingame_name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    data = db.Column(db.String(5000))
    clock_in = db.Column(db.DateTime, nullable=False)
    clock_out = db.Column(db.DateTime)
    active = db.Column(db.Boolean, nullable=False)
    script_id = db.Column(db.Integer, db.ForeignKey("scripts.id"))

    room = db.relationship(Room, foreign_keys=room_id, backref="bots")
    script = db.relationship("Script", foreign_keys=script_id, backref="bots")

    @staticmethod
    def get_bots():
        return db.session.query(Bot)

    @staticmethod
    def get_bots_for_room(web_token):
        return db.session.query(Bot).join(Bot.room).filter(Room.token == web_token)


class Script(db.Model):
    __tablename__ = "scripts"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    script_name = db.Column(db.String(100), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(100), nullable=False)
    script_category = db.Column(db.String(100), nullable=False)
    script_description = db.Column(db.String(1000), nullable=False)
    script_topic = db.Column(db.String(500), nullable=False)
    script_image = db.Column(db.String(1000), nullable=False)

    @staticmethod
    def get_scripts():
        return db.session.query(Script)


class RemoteCommand(db.Model):
    __tablename__ = "remote_command"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(10000))


class CommandToScript(db.Model):
    __tablename__ = "cmd_to_script"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    command_id = db.Column(db.Integer, db.ForeignKey('remote_command.id'))
    script_id = db.Column(db.Integer, db.ForeignKey('scripts.id'))

    command = db.relationship(RemoteCommand, foreign_keys=command_id, backref="cmd_to_scripts")
    script = db.relationship(Script, foreign_keys=script_id, backref='cmd_to_scripts')


class BotCommand(db.Model):
    __tablename__ = "bot_command"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    command_id = db.Column(db.Integer, db.ForeignKey('remote_command.id'))
    bot_id = db.Column(db.Integer, db.ForeignKey('bots.id'))

    command = db.relationship(RemoteCommand, foreign_keys=command_id, backref="commands")
    bot = db.relationship(Bot, foreign_keys=bot_id, backref='commands')


class ProcessingCommands(db.Model):
    __tablename__ = "processing_command"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    bot_id = db.Column(db.Integer, db.ForeignKey('bots.id'))
    command_id = db.Column(db.Integer, db.ForeignKey('remote_command.id'))
    progress_percentage = db.Column(db.Integer)
    progression_message = db.Column(db.String(200))

    command = db.relationship(RemoteCommand, foreign_keys=command_id, backref="processing_commands")
    bot = db.relationship(Bot, foreign_keys=bot_id, backref='processing_commands')


class Announcements(db.Model):
    __tablename__ = "announcements"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.TEXT)
    title = db.Column(db.String(100), nullable=False)
    post_date = db.Column(db.Date)

    @staticmethod
    def get_latest():
        return db.session.query(Announcements).order_by(desc(Announcements.post_date))
