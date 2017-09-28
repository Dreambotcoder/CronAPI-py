from pprint import pprint

from flask import json
import datetime
import requests
from flask import Blueprint, request, abort

from requests.models import json_dumps
from app import db
from app.config import get_website_link
from app.model.dbmodels import Room, Bot

bot_controller = Blueprint('bot_controller', __name__)


@bot_controller.route('/api/room/bots/remove', methods=["POST"])
def remove_bots():
    auth = request.authorization
    alias = request.json.get("alias")
    if authenticate(auth.username, auth.password):
        bot = Bot.get_bots().filter(Bot.ingame_name == alias) \
            .join(Bot.room) \
            .filter(Room.token == auth.username, Room.token_pass == auth.password).first()
        if bot:
            db.session.delete(bot)
            db.session.commit()
            json_dict = {
                "web_token": auth.username,
                "bot_id": bot.id,
                "bot_name" : bot.ingame_name
            }
            requests.post(
                get_website_link() + "/emit/remove",
                json=json_dict
            )
            return "C_D"
        return abort(400)
    else:
        return abort(400)


@bot_controller.route("/api/room/bots/update", methods=["POST"])
def update_bots():
    auth = request.authorization
    pprint(json.dumps(request.json))
    alias = request.json.get("alias")
    data = request.json.get("data")
    if authenticate(auth.username, auth.password):
        bot = Bot.get_bots().filter(Bot.ingame_name == alias) \
            .join(Bot.room) \
            .filter(Room.token == auth.username, Room.token_pass == auth.password).first()
        if bot:
            bot.data = str(json_dumps(data))
            db.session.add(bot)
            db.session.commit()
            json_dict = {
                "bot_id": bot.id,
                "web_token": auth.username,
                "data": json.loads(bot.data)
            }
            pprint(json_dict)
            requests.post(get_website_link() + "/emit/update",  # todo fix this shit
                          json=json_dict
                          )
            return "B_U"
        else:
            return "N_B_F"


@bot_controller.route("/api/room/bots", methods=['POST'])
def put_bots():
    auth = request.authorization
    alias = request.json.get("alias")
    script_id = request.json.get("script_id")
    data = request.json.get("data")
    print json.dumps(alias)
    if authenticate(auth.username, auth.password):
        bots = Bot.get_bots_for_room(auth.username).all()
        for bot in bots:
            if bot.ingame_name == alias:
                return "B_A_E"
        newBot = Bot()
        newBot.ingame_name = alias
        newBot.clock_in = datetime.datetime.utcnow()
        newBot.script_id = script_id
        newBot.active = True
        newBot.ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        newBot.room_id = Room.get_rooms().filter(Room.token == auth.username).first().id
        newBot.data = json.dumps(data)
        db.session.add(newBot)
        db.session.commit()
        json_dict = {
            "web_token": auth.username,
            "bot_alias": newBot.ingame_name,
            "bot_id": int(newBot.id),
            "ip_address": newBot.ip_address,
            "clock_in": str(newBot.clock_in)
        }
        pprint(json_dict)
        requests.post(get_website_link() + "/emit",  # todo fix this shit
                      json=json_dict
                      )
        return "H_U"

    else:
        print ("wrong room credentials")
    return "U_C"


def authenticate(token, token_pass):
    room = Room.get_rooms().filter(Room.token == token, Room.token_pass == token_pass).first()
    return room is not None
