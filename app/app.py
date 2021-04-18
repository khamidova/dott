from flask import Flask
from flask_migrate import Migrate
from models import db
import config

app = Flask(__name__)

# setup database
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)

if __name__ == "__main__":
    app.run()
