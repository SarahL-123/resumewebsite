# the page for adding new pages to the database

# import libraries
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, PasswordField
from wtforms import MultipleFileField, FileField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

# import my own stuff
from app_stuff import db
from ..models import Project


class AddPageForm(FlaskForm):

    tag = StringField("URL to use", validators=[DataRequired()])

    # Not sure if putting in a string that is too long will cause errors...
    title = StringField("Title:", validators=[DataRequired()])

    text = TextAreaField("Text: ", validators=[DataRequired()])
    homepagepicture = FileField(
        "Picture for card on homepage: ",
        validators=[FileAllowed(["jpg", "png", "bmp", "gif"])],
    )

    pictures = MultipleFileField(
        "upload images: ", validators=[FileAllowed(["jpg", "png", "bmp", "gif"])]
    )

    submit = SubmitField("Create new page")

    # Don't forget to add options here to upload pictures eventually

    # Check that the title doesn't already exist in database
    def validate_tag(self, field):
        tag_lowercase = field.data.lower()
        if Project.query.filter_by(tag=tag_lowercase).first():
            raise ValidationError("A page with this URL already exists")
        if field.data.isalnum() == False:
            raise ValidationError(
                "Only alphanumeric characters are allowed, and no spaces"
            )

    def setHeader(self, header):
        self.header = header


class EditPageForm(AddPageForm):
    def setCurrentName(self, name):
        self.currentname = name

    submit = SubmitField("Update page")
    deleteOldPics = BooleanField("Delete old pics?")

    # I need to override this function because:
    # If the page is named 'project1' and the user doesn't change it
    # It will check the database and go 'oh project1 already exists'

    def validate_tag(self, field):
        tag_lowercase = field.data.lower()
        if tag_lowercase == self.currentname:
            return
        if Project.query.filter_by(tag=tag_lowercase).first():
            raise ValidationError("A page with this URL already exists")
        if field.data.isalnum() == False:
            raise ValidationError("Only alphanumeric characters are allowed")


class DeletePageForm(FlaskForm):
    submit_delete = SubmitField("Delete page")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    submit = SubmitField("Login")
