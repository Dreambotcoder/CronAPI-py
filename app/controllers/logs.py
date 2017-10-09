import datetime
from pprint import pprint

import requests
from flask import Blueprint, json, request, abort
from sqlalchemy import func

from app import db
from app.config import get_backend_token
from app.model.dbmodels import BotLog, Room

logs_controller = Blueprint('logs_controller', __name__)


@logs_controller.route('/api/logs/bot', methods=['POST'])
def get_specific_logs():
    web_token = request.json.get("web_token")
    backend_token = request.json.get("backend_token")
    alias = request.json.get("alias")


@logs_controller.route("/api/logs", methods=["POST"])
def get_logs():
    web_token = request.json.get("web_token")
    backend_token = request.json.get("backend_token")
    if backend_token != get_backend_token():
        return abort(401)
    data = {}
    timeline_data = []
    bot_dates = BotLog.get_distinctive_date_logs(
        ).join(
        BotLog.room
    ).filter(
        Room.token == web_token
    ).order_by(
        BotLog.date.desc()
    )
    for log_date in bot_dates:
            logs = []
            logs_for_date = BotLog.get_bot_logs().filter(BotLog.date == log_date[0])
            for log in logs_for_date:
                logs.append(
                    {
                        "id": log.id,
                        "name": log.ingame_name,
                        "ip": log.ip_address,
                        "runtime": log.runtime,
                        # "data": json.loads(log.data)
                    }
                )
            data_dict = {"date": log_date[0], 'logs': logs}
            timeline_data.append(data_dict)
    data['timeline_data'] = timeline_data
    return json.dumps(data, indent=4)


def generate_runtime_by_date(clock_in, clock_out):
    hours = 0
    minutes = 0
    seconds = 0
    one_minute = 60
    one_hour = one_minute * 60
    one_day = one_hour * 24
    diff = clock_out - clock_in
    days = diff.days
    hours += (days * 24)
    total_seconds = diff.seconds
    while total_seconds > 0:
        if total_seconds > one_day:
            days += 1
            total_seconds -= one_day
        elif total_seconds > one_hour:
            hours += 1
            total_seconds -= one_hour
        elif total_seconds > one_minute:
            minutes += 1
            total_seconds -= one_minute
        else:
            seconds += total_seconds
            total_seconds = 0
    hours += (days * 24)
    return "{}h:{}m:{}s".format(str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2))
