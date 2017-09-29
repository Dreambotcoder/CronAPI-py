import datetime
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, json

from app.model.dbmodels import Announcements

util_controller = Blueprint('util_controller', __name__)


@util_controller.route('/api/announcements', methods=["GET"])
def get_announcements():
    announcements = Announcements.get_latest().limit(5)
    data = []
    for announcement in announcements:
        data.append({
            "post_date": announcement.post_date.strftime('%d %B %Y'),
            "text": announcement.text,
            "title": announcement.title
        })
    return json.dumps(data, default=json_serial)


@util_controller.route('/api/loot/<string:npc_name>/', methods=["GET"])
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
