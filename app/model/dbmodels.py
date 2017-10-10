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


class BotSession(db.Model):
    __tablename__ = "bot_sessions"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey(Room.id))
    alias = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    clock_in = db.Column(db.DateTime, nullable=False)
    script_id = db.Column(db.Integer, db.ForeignKey("scripts.id"))
    account_hash = db.Column(db.String(100), db.ForeignKey('bot_hash.hash'))

    room = db.relationship(Room, foreign_keys=room_id, backref="bots")
    script = db.relationship("Script", foreign_keys=script_id, backref="bots")
    bot_hash = db.relationship("BotHash", foreign_keys=account_hash, backref="bot_sessions")

    @staticmethod
    def get_bots():
        return db.session.query(BotSession)

    @staticmethod
    def get_bots_for_room(web_token):
        return db.session.query(BotSession).join(BotSession.room).filter(Room.token == web_token)

    @staticmethod
    def get_by_id(id):
        return db.session.query(BotSession).filter(BotSession.id == id).first()


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
    session_id = db.Column(db.Integer, db.ForeignKey('bot_sessions.id'))

    command = db.relationship(RemoteCommand, foreign_keys=command_id, backref="commands")
    bot = db.relationship(BotSession, foreign_keys=session_id, backref='commands')


class ProcessingCommands(db.Model):
    __tablename__ = "processing_command"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('bot_sessions.id'))
    command_id = db.Column(db.Integer, db.ForeignKey('remote_command.id'))
    progress_percentage = db.Column(db.Integer)
    progression_message = db.Column(db.String(200))

    command = db.relationship(RemoteCommand, foreign_keys=command_id, backref="processing_commands")
    bot = db.relationship(BotSession, foreign_keys=session_id, backref='processing_commands')


class Announcements(db.Model):
    __tablename__ = "announcements"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.TEXT)
    title = db.Column(db.String(100), nullable=False)
    post_date = db.Column(db.Date)

    @staticmethod
    def get_latest():
        return db.session.query(Announcements).order_by(desc(Announcements.post_date))


class BotLog(db.Model):
    __tablename__ = "bot_logs"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey(Room.id))
    ingame_name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    data = db.Column(db.String(5000))
    date = db.Column(db.String(100), nullable=False)
    runtime = db.Column(db.String(1000))
    script_id = db.Column(db.Integer, db.ForeignKey("scripts.id"))

    room = db.relationship(Room, foreign_keys=room_id, backref="bot_logs")
    script = db.relationship("Script", foreign_keys=script_id, backref="bot_logs")

    @staticmethod
    def get_bot_logs():
        return db.session.query(BotLog)

    @staticmethod
    def get_distinctive_date_logs():
        return db.session.query(BotLog.date.distinct())


class Notifications(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    clock_in = db.Column(db.DateTime)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.TEXT)
    bot_id = db.Column(db.Integer, db.ForeignKey(BotSession.id))

    bot = db.relationship(BotSession, foreign_keys=bot_id, backref="notifications")


class BotHash(db.Model):
    __tablename__ = "bot_hash"
    hash = db.Column(db.String(100), primary_key=True, nullable=False)


class SessionData(db.Model):
    __tablename__ = "session_data"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    session_data = db.Column(db.TEXT, nullable=False)
    stat_data = db.Column(db.TEXT)
    clock_in = db.Column(db.DateTime, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey(BotSession.id))

    session = db.relationship(BotSession, foreign_keys=session_id, backref="session_data_block")

    @staticmethod
    def get_recent_data_for_session(session):
        return db.session.query(SessionData).filter(
            SessionData.session == session
        ).order_by(
            desc(
                SessionData.clock_in
            )
        ).first()


class ClientSnapshot(db.Model):
    __tablename__ = "snapshots"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey(BotSession.id))
    base64_img = db.Column(db.TEXT, nullable=False)
    clock_in = db.Column(db.DateTime, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey(Room.id))

    session = db.relationship(BotSession, foreign_keys=session_id, backref="snapshots")
    room = db.relationship(Room, foreign_keys=room_id, backref="snapshots")