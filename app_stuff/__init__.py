# import libraries
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask_login import LoginManager

# import my own stuff
from app_stuff.models import AdminUser

# Set up the app
app = Flask(__name__)

app.config["SECRET_KEY"] = "mysecretkey"  # update this later

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL"
) or "sqlite:///" + os.path.join(basedir, "mydatabase.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#I put the S3 keys in here
app.config.from_object("config")

# Set up the database and migrations
from .models import db

db.init_app(app)
Migrate(app, db)


# directory for pictures (note that the nested os.path.dirname() is used to go to the directory ABOVE it)
pic_directory = os.path.join(app.root_path, "static\project_pics")
os.makedirs(pic_directory, exist_ok=True)


# set up the log ins
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin.login"

# user loader function that takes ID and gives the user
# Is required by Flask
@login_manager.user_loader
def load_user(id):
    return AdminUser.query.get(int(id))


# register the blueprints
from app_stuff.core.views import core_blueprint

app.register_blueprint(core_blueprint, url_prefix="/")

from app_stuff.projects.views import projects_blueprint

app.register_blueprint(projects_blueprint, url_prefix="/projects")

from app_stuff.admin.views import admin_blueprint

app.register_blueprint(admin_blueprint, url_prefix="/admin")


# custom 404 page
@app.errorhandler
def custom_404_page():
    return render_template("404.html")
