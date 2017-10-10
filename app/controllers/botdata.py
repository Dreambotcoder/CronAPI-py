from pprint import pprint

import math
from flask import json
import datetime
import requests
from flask import Blueprint, request, abort

from requests.models import json_dumps
from app import db
from app.config import get_website_link
from app.controllers.logs import generate_runtime_by_date
from app.model.dbmodels import Room, BotSession, BotLog, Notifications, SessionData

bot_controller = Blueprint('bot_controller', __name__)


@bot_controller.route('/api/room/bots/remove', methods=["POST"])
def remove_bots():
    auth = request.authorization
    alias = request.json.get("alias")
    if authenticate(auth.username, auth.password):
        bot = BotSession.get_bots().filter(BotSession.alias == alias) \
            .join(BotSession.room) \
            .filter(Room.token == auth.username, Room.token_pass == auth.password).first()
        if bot:
            botlog = BotLog()
            botlog.ingame_name = bot.ingame_name
            botlog.script_id = bot.script_id
            botlog.data = bot.data
            botlog.ip_address = bot.ip_address
            botlog.date = bot.clock_in.date().strftime('%m/%d/%Y')
            botlog.runtime = generate_runtime_by_date(bot.clock_in, datetime.datetime.now())
            botlog.room_id = bot.room_id
            db.session.add(botlog)
            db.session.delete(bot)
            db.session.commit()
            json_dict = {
                "web_token": auth.username,
                "bot_id": bot.id,
                "bot_name": bot.alias
            }
            requests.post(
                get_website_link() + "/emit/remove",
                json=json_dict
            )
            return "C_D"
        return abort(400)
    else:
        return abort(400)


@bot_controller.route('/api/room/bots/shout/put', methods=["POST"])
def get_shouts():
    auth = request.authorization
    web_token = auth.username
    if authenticate(web_token, auth.password):
        alias = request.json.get("alias")
        bot = BotSession.get_bots_for_room(web_token).filter(BotSession.alias == alias).first()
        if bot:
            title = request.json.get("title")
            text = request.json.get("text")
            clock_in = datetime.datetime.utcnow()
            notif = Notifications()
            notif.clock_in = clock_in
            notif.bot_id = bot.id
            notif.text = text
            notif.title = title
            db.session.add(notif)
            db.session.commit()
            return ""
        else:
            return abort(200)
    else:
        return abort(401)


@bot_controller.route("/api/room/bots/update", methods=["POST"])
def update_bots():
    auth = request.authorization
    alias = request.json.get("alias")
    data = request.json.get("data")
    if authenticate(auth.username, auth.password):
        session = BotSession.get_bots().filter(BotSession.alias == alias) \
            .join(BotSession.room) \
            .filter(Room.token == auth.username, Room.token_pass == auth.password).first()
        if session:
            data_entry = SessionData()
            data_entry.clock_in = datetime.datetime.utcnow()
            data_entry.session_data = json_dumps(data)
            data_entry.session_id = session.id
            data_entry.stat_data = json_dumps(request.json.get("skills"))
            db.session.add(data_entry)
            db.session.commit()
            pprint(json_dumps(data))
            json_dict = {
                "bot_id": session.id,
                "web_token": auth.username,
                "data": json_dumps(data),
                "stat_data": json_dumps(request.json.get("skills"))
            }
            pprint(json_dict)
            requests.post(get_website_link() + "/emit/update",  # todo fix this shit
                          json=json_dict
                          )
            return "B_U"
        else:
            return "N_B_F"


@bot_controller.route("/api/levels")
def levels_test():
    points = 0
    for level in range(1, 100):
        diff = int(level + 300 * math.pow(2, float(level) / 7))
        points += diff
        str = "Level %d = %d" % (level + 1, points / 4)
        print str

    return ""


@bot_controller.route("/api/room/bots", methods=['POST'])
def put_bots():
    auth = request.authorization
    alias = request.json.get("alias")
    script_id = request.json.get("script_id")
    data = request.json.get("data")
    print json.dumps(alias)
    if authenticate(auth.username, auth.password):
        bots = BotSession.get_bots_for_room(auth.username).all()
        for bot in bots:
            if bot.alias == alias:
                return "B_A_E"
        newBot = BotSession()
        newBot.alias = alias
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
            "bot_alias": newBot.alias,
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
