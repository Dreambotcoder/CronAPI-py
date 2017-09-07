from flask import Blueprint, json
import datetime
import requests
from flask import Blueprint, request, abort, render_template

from requests.models import json_dumps
from app import db
from app.model.dbmodels import Room, Bot

bot_controller = Blueprint('bot_controller', __name__)


@bot_controller.route("/api/room/bots/update", methods=["POST"])
def update_bots():
    auth = request.authorization
    alias = request.json.get("alias")
    data = request.json.get("data")
    if authenticate(auth.username, auth.password):
        bot = Bot.get_bots().filter(Bot.ingame_name == alias) \
            .join(Bot.room) \
            .filter(Room.token == auth.username, Room.token_pass == auth.password).first()
        if bot:
            bot.data = data
            db.session.add(bot)
            db.session.commit()
            return "B_U"
        else:
            return "N_B_F"


@bot_controller.route("/api/room/bots", methods=['POST'])
def put_bots():
    auth = request.authorization
    alias = request.json.get("alias")
    script_id = request.json.get("script_id")
    data = request.json.get("data")
    print json.dumps(data)
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
        return "H_U"

    else:
        print ("wrong room credentials")
    return "U_C"


def authenticate(token, token_pass):
    room = Room.get_rooms().filter(Room.token == token, Room.token_pass == token_pass).first()
    return room is not None
