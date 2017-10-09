from functools import wraps

from flask import request, abort

from app.model.dbmodels import Room


def requires_auth_header(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        room = Room.get_rooms().filter(Room.token == auth.username, Room.token_pass == auth.password).first()
        if room is None:
            return abort(401)
    return wrapper


def requires_auth_json(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        username = request.json.get("web_token")
        password = request.json.get("token_pass")
        room = Room.get_rooms().filter(Room.token == username, Room.token_pass == password).first()
        return room is not None
    return wrapper
