import datetime
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, request, abort, render_template

from requests.models import json_dumps
from app import db
from app.model.rooms import Room
from app.model.bot import Bot
from app.model.bot import Script

api_controller = Blueprint('api', __name__)


@api_controller.route('/')
def hello_world():
    return "<h1>Welcome to CronAPI</h1>" \
           "<br>" \
           "<h3>Contact Articron if you want to use this API</h3>"


@api_controller.route("/api/scripts/", methods=['POST'])
def get_script():
    data = request.form
    script_id = data['id']
    script = Script.get_scripts().filter(Script.id == script_id).first()
    response = {}
    script_data = [{
        "script_id": script.id,
        "script_name": script.script_name,
        "script_author": script.author_name
    }]

    response['status_code'] = 200
    response['message'] = "Script details for script with id " + script_id
    response['script_data'] = script_data
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


@api_controller.route("/api/rooms/add", methods=['POST'])
def add_room():
    data = request.form
    web_token = data["token"]
    token_pass = data['pass']
    room = Room.get_rooms().filter(Room.token == web_token).first()
    if room is not None:
        return "A_E"
    else:
        toAdd = Room()
        toAdd.token = web_token
        toAdd.token_pass = token_pass
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


@api_controller.route("/api/authenticate/form", methods=["POST"])
def check_room():
    frm = request.form
    web_token = frm['web_token']
    token_pass = request.form.get("token_pass")
    room = Room.get_rooms().filter(Room.token == web_token).first()
    if room is not None:
        if room.token_pass == token_pass:
            return " "
    return abort(400)


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


@api_controller.route('/cronfighter/new/', methods=['GET'])
def create_fighter_ui():
    return render_template("fighter_settings.html")


# JSON serializer for objects not serializable by default json code
def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.strftime("%Y-%m-%d %H:%M:%S")
        return serial
    elif isinstance(obj, datetime.date):
        serial = obj.strftime("%Y-%m-%d")
        return serial
    raise TypeError("Type not serializable")
