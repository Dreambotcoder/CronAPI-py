import datetime
from pprint import pprint

import pygal
from flask import Blueprint, request, abort, json
from pygal import Line
from pygal.style import DarkStyle, Style

from requests.models import json_dumps
from app import db
from app.config import get_backend_token
from app.decorators import requires_auth_header
from app.model.dbmodels import Script, Room, BotSession, SessionData, ClientSnapshot

api_controller = Blueprint('api', __name__)


@api_controller.route('/heartbeat')
def heartbeat():
    return "ALIVE"


@api_controller.route("/api/skills/levels", methods=["POST"])
def levels():
    bot_id = request.json.get("bot_id")
    backend_token = request.json.get("backend_token")
    sessionData = SessionData.get_recent_data_for_session(BotSession.get_by_id(bot_id))
    if sessionData:
        return json_dumps(json.loads(sessionData.stat_data), default=json_serial)
    return abort(401)


@api_controller.route("/api/snapshots/specific/list", methods=["POST"])
def specific_snapshots():
    session_id = request.json.get("bot_id")
    backend_token = request.json.get("backend_token")
    snapshots = ClientSnapshot.get_snapshots_for_session_id(session_id)
    snapshots_container = []
    for snapshot in snapshots:
        snapshots_container.append({
            "id": snapshot.id,
            "clock_in": snapshot.clock_in
        })
    return json.dumps(snapshots_container, default=json_serial)


@api_controller.route("/api/snapshots/specific/base64", methods=["POST"])
def base64_snapshot():
    session_id = request.json.get("bot_id")
    snapshot_id = request.json.get("snapshot_id")
    snapshot = ClientSnapshot.get_snapshots_for_session_id(session_id).filter(ClientSnapshot.id == snapshot_id).first()
    if snapshot:
        return snapshot.base64_img


@api_controller.route('/api/list/commands', methods=["POST"])
def command_list():
    script_key = request.json.get("api_key")
    script = Script.get_scripts().filter(Script.api_key == script_key).first()
    data = {}
    commands = []
    if script:
        for command in script.cmd_to_scripts:
            commands.append(command.command.name)
        data["commands"] = commands
        return json.dumps(data, default=json_serial)
    return abort(400)


@api_controller.route('/')
def hello_world():
    return "<h1>Welcome to CronAPI 0.0.1</h1>" \
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
    bot_data = []  #
    notif_data = []
    session = BotSession.get_bots().filter(BotSession.id == bot_id).join(BotSession.room).filter(
        Room.token == web_token).first()
    if session is None:
        return abort(400)
    data_block = SessionData.get_recent_data_for_session(session)
    for notification in session.notifications:
        notif_data.append({
            "title": notification.title,
            "text": notification.text,
            "timestamp": notification.clock_in
        })

    snapshots = ClientSnapshot.get_snapshots_for_session_id(bot_id)

    snapshots_container = []
    for snapshot in snapshots.all():
        snapshots_container.append({
            "id": snapshot.id,
            "clock_in": snapshot.clock_in,
            "name": snapshot.name
        })

    bot_data.append({
        "bot_name": session.alias,
        "ip_address": session.ip_address,
        "game_data": json.loads(data_block.session_data),
        "stat_data": json.loads(data_block.stat_data),
        "clock_in": session.clock_in,
        "script_id": session.script_id,
        "notifications": notif_data,
        "snapshots": snapshots_container
    })

    response['bot_data'] = bot_data
    return json_dumps(response, default=json_serial)


@api_controller.route('/api/bots/web/format/remote', methods=['POST'])
def get_compact_bots_for_room():
    bots = BotSession.get_bots()
    response = {}
    bot_data = []
    processed_data = []
    polling_data = []
    web_token = request.json.get("web_token")
    script_id = request.json.get("script_id")
    all_bots = bots.join(BotSession.room).filter(Room.token == web_token).filter(Room.script_id == script_id)
    for bot in all_bots.all():
        processing_command = bot.processing_commands
        polling_command = bot.commands
        if processing_command and len(processing_command) > 0:
            command = processing_command[0]
            processed_data.append({
                "bot_name": bot.ingame_name,
                "remote_percentage": command.progress_percentage,
                "remote_message": command.progression_message,
                "remote_command": command.command.name
            })
        elif polling_command and len(polling_command) > 0:
            polling_data.append({
                "bot_name": bot.ingame_name,
                "remote_command": polling_command[0].command.name
            })
        else:
            bot_data.append({
                "bot_id": bot.id,
                "bot_name": bot.alias
            })
    response['available'] = bot_data
    response['processing'] = processed_data
    response['polling'] = polling_data
    return json_dumps(response, default=json_serial)


@api_controller.route("/api/bots/web", methods=['POST'])
def get_bots_for_room_web():
    bots = BotSession.get_bots()
    response = {}
    bot_data = []
    web_token = request.json.get("web_token")
    filtered_bots = bots.join(BotSession.room).filter(Room.token == web_token)

    for bot in filtered_bots.all():
        bot_data.append({
            "bot_id": bot.id,
            "bot_name": bot.alias,
            "ip_address": bot.ip_address,
            "game_data": json.loads(SessionData.get_recent_data_for_session(bot).session_data),
            "script_id": bot.script_id,
            "hash": str(bot.bot_hash.hash)
        })
    response['bot_data'] = bot_data
    response['status_code'] = 200
    response['message'] = "All bots for web token " + web_token
    return json_dumps(response, default=json_serial)


@api_controller.route("/api/bots/", methods=['POST'])
def get_bots_for_room():
    bots = BotSession.get_bots()
    data = request.form
    response = {}
    bot_data = []
    web_token = data['token']
    filtered_bots = bots.join(BotSession.room).filter(Room.token == web_token)

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
@requires_auth_header
def add_room():
    web_token = request.authorization.username
    token_pass = request.authorization.password
    script_id = request.json.get("script_id")
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


@api_controller.route("/api/pygal/test")
def pygal_test():
    cron_style = Style(
        background="transparent",
        plot_background='transparent',
        foreground='#f5f5f5',
        foreground_strong='#2ecc71',
        foreground_subtle='#2ecc71',
        colors=('#2ecc71', '#E8537A', '#E95355', '#E87653', '#E89B53'),
        font_family='googlefont:Open Sans'
    )
    graph = Line(style=cron_style,interpolate='cubic')

    graph.title = 'Strength XP progression'
    all_data_for_session = SessionData.get_all_data_for_session(21).limit(100)
    date_block = []
    stat_block = []
    for datablock in all_data_for_session:
        stat = json.loads(datablock.stat_data)
        date_block.append(datablock.clock_in.strftime("%Y-%m-%d %H:%M:%S"))
        stat_block.append(stat.get("Strength").get("current_xp"))
    graph.x_labels = date_block
    graph.add('Strength xp', stat_block)
    return graph.render_data_uri()

@api_controller.route("/api/room/exists", methods=['POST'])
def room_exists():
    frm = request.form
    web_token = frm['token']
    room = Room.get_rooms().filter(Room.token == web_token).first()
    if room is None:
        return "I_F"
    return "A_E"


@api_controller.route("/api/script/authenticate", methods=["POST"])
@requires_auth_header
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
    room = Room.get_rooms().filter(Room.token == web_token).first()
    if room is not None:
        if room.token_pass == token_pass:
            return str(room.script.id)
    return abort(400)


@api_controller.route("/api/backend/all_scripts", methods=['POST'])
def get_all_scripts():
    backend_token = request.json.get("backend-token")
    web_token = request.json.get("web_token")
    count = BotSession.get_bots().join(BotSession.room).filter(Room.token == web_token).count()
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
        response['bot_count'] = count
        return json_dumps(response, default=json_serial)


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
