import requests
from flask import Blueprint, request, abort, json

from app import db
from app.config import get_website_link
from app.controllers.api import json_serial, authenticate
from app.model.dbmodels import Bot, Room, Script

remote_controller = Blueprint('emitter_controller', __name__)


@remote_controller.route('/api/remote/check', methods=["POST"])
def check_bot_cmd():
    bot_alias = request.json.get("bot_alias")
    web_token = request.authorization.username
    token_pass = request.authorization.password
    if authenticate(web_token, token_pass):
        bot = Bot.get_bots(
        ).join(
            Bot.room
        ).filter(
            Room.token == web_token
        ).filter(
            Bot.ingame_name == bot_alias
        ).first()
        if bot:
            if len(bot.commands) <= 0:
                return ""
            command_context = bot.commands[0]
            cmd_name = command_context.command.name
            db.session.delete(command_context)
            db.session.commit()
            return cmd_name
        else:
            return ""
    else:
        return abort(401)


@remote_controller.route('/api/remote/update/process', methods=["POST"])
def update_remote_process():
    web_token = request.authorization.username
    if authenticate(web_token, request.authorization.password):
        bot_alias = request.json.get("bot_alias")
        command = request.json.get("command")
        report_message = request.json.get("report_message")
        report_percentage = str(request.json.get("report_percentage"))
        bot = Bot.get_bots().filter(Bot.ingame_name == bot_alias).first()
        if bot:
            if bot.processing_commands:
                command_entry = bot.processing_commands[0]
                if command_entry.command.name == command:
                    command_entry.progression_message = report_message
                    command_entry.progress_percentage = int(report_percentage)
                    db.session.add(command_entry)
                    db.session.commit()
                    print 'committed'
                    data_dict = {
                        "bot_id": bot.id,
                        "bot_name": bot.ingame_name,
                        "web_token": web_token,
                        "percentage": report_percentage,
                        "message": report_message
                    }
                    print 'posting'
                    try:
                        requests.post(get_website_link() + "/emit/remote/process", json=data_dict)
                    except Exception as e:
                        print e
                    print 'posted'
                return "OK"
        return abort(401)


@remote_controller.route('/api/remote', methods=["POST"])
def remote():
    script_id = request.json.get("script_id")
    script = Script.get_scripts().filter(Script.id == script_id).first()
    commands = []
    for command in script.cmd_to_scripts:
        commands.append({
            "name": command.command.name,
            "description": command.command.description
        })
    return json.dumps(commands, default=json_serial)

