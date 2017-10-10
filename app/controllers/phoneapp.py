from pprint import pprint

from flask import Blueprint, request, abort, json
from app import db
from app.model.dbmodels import Room, Script, BotSession

phone_controller = Blueprint("phone_controller", __name__)


@phone_controller.route("/phone/login", methods=["POST"])
def login():
    auth = request.authorization
    room_name = auth.username
    pass_token = auth.password
    room = Room.get_rooms().filter(Room.token == room_name, Room.token_pass == pass_token).first()
    if room is None:
        abort(400)
    return ""


@phone_controller.route("/phone/botlist/<int:id>", methods=["POST"])
def botlist_concrete(id):
    auth = request.authorization
    game_data = {}
    if authenticate(auth.username,auth.password):
        bot = BotSession.get_bots().filter(BotSession.id == id).join(BotSession.room).filter(Room.token == auth.username).first()

        data = json.loads(bot.data)
        if bot:
            game_data = {
                "alias" : bot.ingame_name,
                "ip" : bot.ip_address,
                "clock_in" : bot.clock_in,
                "data" : data
            }
        else:
            abort(400)
        print json.dumps(game_data)
        return json.dumps(game_data)
    else:
        abort(400)
    pass


@phone_controller.route("/phone/botlist", methods=["POST"])
def botlist():
    auth = request.authorization
    data = {}
    botlist = []
    if authenticate(auth.username, auth.password):
        script = Script.get_scripts().join(Script.rooms).filter(Room.token == auth.username,
                                                                Room.token_pass == auth.password).first()
        bots = BotSession.get_bots_for_room(auth.username).all()
        if script and bots:
            script_info = {
                "name": script.script_name,
                "author": script.author_name,
                "count": len(bots)
            }
            for bot in bots:
                botlist.append({
                    "alias": bot.ingame_name,
                    "id": bot.id,
                    "ip": bot.ip_address
                })
            data["script_info"] = script_info
            data["botlist"] = botlist
            print json.dumps(data)
            return json.dumps(data)
    else:
        print ("else'd")
        abort(400)


def authenticate(token, token_pass):
    room = Room.get_rooms().filter(Room.token == token, Room.token_pass == token_pass).first()
    return room is not None
