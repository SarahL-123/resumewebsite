from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(64), index=True, unique=True)
    title = db.Column(db.String(128), index=True)

    text = db.Column(db.String(1000))

    pictures = db.relationship("Image", backref="project", lazy=True, uselist=False)

    def __init__(self, tag, title, text, pictures=None):
        self.tag = tag
        self.title = title
        self.text = text

        if pictures:
            self.pictures = pictures


# I am storing the file names of the uploaded images
# The actual images are just in a folder
# See admin > views for where it goes
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64), nullable=False)
    small_for_homepage = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)

    def __init__(self, filename, project_id, forhomepage):
        self.filename = filename
        self.project_id = project_id
        self.small_for_homepage = forhomepage

    def __repr__(self):
        return self.filename


class AdminUser(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # for creating a new admin user
    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, pw_to_check):
        return check_password_hash(self.password_hash, pw_to_check)
