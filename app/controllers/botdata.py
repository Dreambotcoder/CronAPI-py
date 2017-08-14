from flask import Blueprint
import datetime
import requests
from flask import Blueprint, request, abort, render_template

from requests.models import json_dumps
from app import db

bot_controller = Blueprint('bot_controller', __name__)


@bot_controller.route("/api/room/bots", methods=['GET'])
def getter_bots():
    return "k"


@bot_controller.route("/api/room/bots", methods=['PUT'])
def put_bots():
    auth = request.authorization

