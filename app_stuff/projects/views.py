# import libraries
from flask import Blueprint, render_template, redirect, url_for, request
import os
import textile

# import my other stuff
from app_stuff.models import Project, Image
from app_stuff import app, db, pic_directory

projects_blueprint = Blueprint("projects", __name__, template_folder="templates")


@projects_blueprint.route("/<project_name>")
def projectpage(project_name):

    # check if the page exists in the database even
    project_name = str(project_name).lower()
    myproject = Project.query.filter_by(tag=project_name).first()

    # if not in the database then go home for now (later I will add custom 404 page)
    if not myproject:
        return render_template("404.html"), 404

    # check if there are any pictures
    pictures = Image.query.filter_by(
        project_id=myproject.id, small_for_homepage=False
    ).all()

    # print("here are the list of picture urls")
    # print(piclist)
    # print("----------")

    # use textile to format the text (so I can have hyperlinks in it!)
    plaintext = myproject.text
    formattedtext = textile.textile(plaintext)

    print(app.config["S3_LOCATION"])
    return render_template(
        "oneproject.html",
        project=myproject,
        piclist=pictures,
        formattedtext=formattedtext,
        S3_LOCATION=app.config["S3_LOCATION"],
    )


@projects_blueprint.app_errorhandler(404)
def error404(e):
    return render_template("404.html"), 404
