from pprint import pprint

from configobj import ConfigObj

CONFIG_FILE = "./config.ini"


def get_database_uri():
    config = ConfigObj(CONFIG_FILE)
    db = config["dbi"]
    db_connection = "%s://%s:%s@%s:%s/%s" % (db["protocol"],
                                             db['username'],
                                             db['password'],
                                             db["host"],
                                             db['port'],
                                             db['database']
                                             )
    return db_connection


def get_backend_token():
    config = ConfigObj(CONFIG_FILE)
    db = config["backend-token"]
    return db["token"]


def get_website_link():
    config = ConfigObj(CONFIG_FILE)
    db = config["website"]
    return db["link"]
