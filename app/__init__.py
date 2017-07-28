from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import get_database_uri

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
db = SQLAlchemy(app)

from controllers.api import api_controller

app.register_blueprint(api_controller)


@app.before_first_request
def create_db():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='localhost')
