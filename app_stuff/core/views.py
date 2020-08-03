
# Import other peoples stuff
from app_stuff import db, app
from flask import render_template, Blueprint, url_for
import os
import re
import textile

# Import my own stuff
from ..models import Project, Image
from app_stuff import pic_directory


core_blueprint = Blueprint("core", __name__, template_folder="templates")

# Home page views
@core_blueprint.route("")
def home():
    # get all the projects
    allprojects = Project.query.order_by(Project.title.asc()).all()

    project_image_tuple = []

    for oneproject in allprojects:

        # get an image
        projectimage = Image.query.filter_by(
            project_id=oneproject.id, small_for_homepage=True
        ).first()

        if projectimage is not None:
            #this one is for the static folder but now we are using AWS S3
            # fullpath = url_for(
            #     "static", filename="project_pics/" + projectimage.filename
            # )

            # Use the one on AWS
            fullpath = app.config['S3_LOCATION'] + projectimage.filename

        else:
            fullpath = app.config['S3_LOCATION'] + "noimage.png"

        # Use textile to convert into html tags and stuff
        project_text = textile.textile(oneproject.text)

        # Use regex to remove the html, leaving only unformatted text
        project_text = re.sub(re.compile("<.*?>"), "", project_text)

        # combine them into a tuple
        project_image_tuple.append((oneproject, fullpath, project_text))

    # print(project_image_tuple)
    return render_template("home.html", data_tuple=project_image_tuple)


@core_blueprint.app_errorhandler(404)
def error404(e):
    return render_template("404.html"), 404
