from flask import Flask
from flask_migrate import Migrate
from .models import db
from .views import views
from .config import SQLALCHEMY_DATABASE_URI
from .cli import import_cli, generate_cli

app = Flask(__name__)

# setup database
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)

# add views
app.register_blueprint(views)

# add cli commands
app.cli.add_command(import_cli)
app.cli.add_command(generate_cli)

if __name__ == "__main__":
    app.run()
