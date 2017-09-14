import datetime
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, request, abort, render_template, json

from requests.models import json_dumps
from app import db
from app.config import get_backend_token
from app.model.dbmodels import Script, Room, Bot

api_controller = Blueprint('api', __name__)


@api_controller.route('/heartbeat')
def heartbeat():
    return "ALIVE"


@api_controller.route('/')
def hello_world():
    return "<h1>Welcome to CronAPI 1.3</h1>" \
           "<br>" \
           "<h3>Contact Articron if you want to use this API</h3>"


@api_controller.route("/api/script_for_room", methods=['POST'])
def get_script_for_room():
    web_token = request.json.get("web_token")
    script = Script.get_scripts().join(Script.rooms).filter(Room.token == web_token).first()
    response = {}
    if script is not None:
        script_data = [{
            "script_id": script.id,
            "script_name": script.script_name,
            "script_author": script.author_name,
            "script_category": script.script_category
        }]
        response['status_code'] = 200
        response['script_data'] = script_data
    response['status_code'] = 400
    print json_dumps(response, default=json_serial)
    return json_dumps(response, default=json_serial)


@api_controller.route("/api/scripts/", methods=['POST'])
def get_script():
    data = request.form
    script_id = data['id']
    script = Script.get_scripts().filter(Script.id == script_id).first()
    response = {}
    script_data = [{
        "script_id": script.id,
        "script_name": script.script_name,
        "script_author": script.author_name,
        "script_category": script.script_category
    }]

    response['status_code'] = 200
    response['message'] = "Script details for script with id " + script_id
    response['script_data'] = script_data

    return json_dumps(response, default=json_serial)


@api_controller.route("/api/bots/specific", methods=['POST'])
def get_specific_bot():
    web_token = request.json.get("web_token")
    bot_id = request.json.get("bot_id")
    response = {}
    bot_data = [] #
    print "BOT_ID = " + str(bot_id)
    bot = Bot.get_bots().filter(Bot.id == bot_id).join(Bot.room).filter(Room.token == web_token).first()
    if bot is None:
        return abort(400)
    data = json.loads(bot.data)
    bot_data.append({
        "bot_name": bot.ingame_name,
        "ip_address": bot.ip_address,
        "game_data": data,
        "clock_in": bot.clock_in,
        "clock_out": bot.clock_out,
        "active": bot.active,
        "script_id": bot.script_id
    })
    response['bot_data'] = bot_data
    print json_dumps(response, default=json_serial)
    return json_dumps(response, default=json_serial)


@api_controller.route("/api/bots/web", methods=['POST'])
def get_bots_for_room_web():
    bots = Bot.get_bots()
    response = {}
    bot_data = []
    web_token = request.json.get("web_token")
    filtered_bots = bots.join(Bot.room).filter(Room.token == web_token)

    for bot in filtered_bots.all():
        bot_data.append({
            "bot_id" : bot.id,
            "bot_name": bot.ingame_name,
            "ip_address": bot.ip_address,
            "game_data": bot.data,
            "clock_in": bot.clock_in,
            "clock_out": bot.clock_out,
            "active": bot.active,
            "script_id": bot.script_id
        })
    response['bot_data'] = bot_data
    response['status_code'] = 200
    response['message'] = "All bots for web token " + web_token
    print json_dumps(response, default=json_serial)
    return json_dumps(response, default=json_serial)


@api_controller.route("/api/bots/", methods=['POST'])
def get_bots_for_room():
    bots = Bot.get_bots()
    data = request.form
    response = {}
    bot_data = []
    web_token = data['token']
    filtered_bots = bots.join(Bot.room).filter(Room.token == web_token)

    for bot in filtered_bots.all():
        bot_data.append({
            "bot_name": bot.ingame_name,
            "ip_address": bot.ip_address,
            "game_data": bot.data,
            "clock_in": bot.clock_in,
            "clock_out": bot.clock_out,
            "active": bot.active,
            "script_id": bot.script_id
        })
    response['bot_data'] = bot_data
    response['status_code'] = 200
    response['message'] = "All bots for web token " + web_token
    return json_dumps(response, default=json_serial)


@api_controller.route("/api/rooms/create", methods=['POST'])
def add_room():
    web_token = request.authorization.username
    token_pass = request.authorization.password
    script_id = request.json.get("script_id")
    print str(script_id)
    room = Room.get_rooms().filter(Room.token == web_token).first()
    if room is not None:
        return "A_E"
    else:
        toAdd = Room()
        toAdd.token = web_token
        toAdd.token_pass = token_pass
        toAdd.script_id = script_id
        db.session.add(toAdd)
        db.session.commit()
    return "C"


@api_controller.route("/api/room/exists", methods=['POST'])
def room_exists():
    frm = request.form
    web_token = frm['token']
    room = Room.get_rooms().filter(Room.token == web_token).first()
    if room is None:
        return "I_F"
    return "A_E"


@api_controller.route("/api/script/authenticate", methods=["POST"])
def auth_room():
    web_token = request.authorization.username
    token_pass = request.authorization.password
    room = Room.get_rooms().filter(Room.token == web_token).first()
    if room is not None:
        if room.token_pass == token_pass:
            return "L_I"
        else:
            return "I_C"
    return "N_E"

@api_controller.route("/api/authenticate", methods=['POST'])
def check_room():
    web_token = request.json.get("web_token")
    token_pass = request.json.get("token_pass")
    print web_token
    print token_pass
    room = Room.get_rooms().filter(Room.token == web_token).first()
    if room is not None:
        if room.token_pass == token_pass:
            print "valid credentials entered: [" + web_token + " : " + token_pass + "]"
            return " "
    print "incorrect credentials"
    return abort(400)


@api_controller.route("/api/authenticate/form", methods=["POST"])
def check_room_by_form():
    frm = request.form
    web_token = frm['web_token']
    token_pass = request.form.get("token_pass")
    room = Room.get_rooms().filter(Room.token == web_token).first()
    if room is not None:
        if room.token_pass == token_pass:
            return " "
    return abort(400)


@api_controller.route("/api/backend/all_scripts", methods=['POST'])
def get_all_scripts():
    backend_token = request.json.get("backend-token")
    response = {}
    result = []
    if backend_token != get_backend_token():
        return abort(400)
    else:
        scripts = Script.get_scripts()
        for script in scripts.limit(4).all():  # todo add DESC by time
            result.append({
                "script_id": script.id,
                "script_name": script.script_name,
                "script_category": script.script_category,
                "script_author": script.author_name,
                "script_description": script.script_description,
                "script_topic_url": script.script_topic,
                "script_image": script.script_image
            })
        response['result'] = result
        return json_dumps(response, default=json_serial)


@api_controller.route('/api/loot/<string:npc_name>/', methods=["GET"])
def get_drops(npc_name):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "connection": "keep-alive",
        'Accept-Encoding': 'identity, deflate, compress, gzip',
        "accept": "Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "cache-control": "max-age=0"
    }
    request = requests.get("http://oldschoolrunescape.wikia.com/wiki/" + npc_name, headers=headers, stream=True)
    text = ""
    for line in request.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            text += decoded_line.encode("utf-8") + " \n"
    soup = BeautifulSoup(text, "html.parser")
    tables = soup.findAll("table", class_="dropstable")
    row_id = 0
    item_name = ""
    item_quantity = ""
    drop_rarity = ""
    wiki_price = ""
    toReturn = ""
    for table in tables:
        for row in table.findAll("td"):
            row_text = row.text.replace("\n", "")
            if row_text is not None or row_text is not "" or row_text != "":

                if row_id % 5 == 0:
                    pass
                if row_id % 5 == 1:
                    item_name = row_text
                if row_id % 5 == 2:
                    item_quantity = row_text
                if row_id % 5 == 3:
                    drop_rarity = row_text
                if row_id % 5 == 4:
                    wiki_price = row_text

                if item_quantity != "" and item_name != "" and drop_rarity != "" and wiki_price != "":
                    toReturn += item_name.strip() + "|" \
                                + item_quantity.strip() + "|" \
                                + drop_rarity.strip() + "|" \
                                + wiki_price.strip() + "\n"
                    item_name = ""
                    item_quantity = ""
                    drop_rarity = ""
                    wiki_price = ""
            row_id += 1
    return toReturn


# JSON serializer for objects not serializable by default json code
def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.strftime("%Y-%m-%d %H:%M:%S")
        return serial
    elif isinstance(obj, datetime.date):
        serial = obj.strftime("%Y-%m-%d")
        return serial
    raise TypeError("Type not serializable")


def authenticate(token, token_pass):
    room = Room.get_rooms().filter(Room.token == token, Room.token_pass == token_pass).first()
    return room is not None