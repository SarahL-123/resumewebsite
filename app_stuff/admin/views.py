from flask import Blueprint, render_template, redirect, url_for, request, flash, request
import os
from flask_login import current_user, login_user, logout_user, login_required
from is_safe_url import is_safe_url
import os
from werkzeug.security import check_password_hash, generate_password_hash

# import my own stuff
from app_stuff import db, app, pic_directory
from app_stuff.models import Project, Image, AdminUser
from .forms import *
from .s3helpers import delete_file_from_s3, upload_file_to_s3

admin_blueprint = Blueprint("admin", __name__, template_folder="templates")


@admin_blueprint.route("/addpage", methods=["GET", "POST"])
@login_required
def addpage():
    form = AddPageForm()

    if form.validate_on_submit():
        # Get the data from the form
        tag = str(form.tag.data).lower()
        title = form.title.data
        text = form.text.data

        myproject = Project(tag, title, text)
        db.session.add(myproject)

        # Flush to database so I can get the primary key
        db.session.flush()

        # now myproject.id will be the primary key of the project.

        ###### NAMING SCHEME FOR PICTURES #####
        # If the primary key is 1 (for example), the images will be saved as
        # 1_0, 1_1, 1_2 and so on.
        # I'm just going to do it like this for now so I can change the title if I want to
        # the picture for the home page is saved as 1_homepage

        # This is the counter for the suffix
        counter = 0

        savePictures([form.homepagepicture.data], myproject.id, forhomepage=True)
        savePictures(form.pictures.data, myproject.id, counter=counter)
        db.session.commit()

        # Return to home page (not really sure where I should link this for now)
        return redirect(url_for("core.home"))

    form.setHeader("Add a project")
    return render_template("addpage.html", form=form)


@admin_blueprint.route("/edit/<pagetitle>", methods=["GET", "POST"])
@login_required
def editpage(pagetitle):
    form = EditPageForm()
    deleteform = DeletePageForm()
    form.setCurrentName(pagetitle)

    # check if the page actually exists
    myproject = Project.query.filter_by(tag=pagetitle).first()
    if not myproject:
        return render_template("404.html"), 404

    if deleteform.validate_on_submit() and deleteform.submit_delete.data:
        deletepage(pagetitle)
        return redirect(url_for("core.home"))

    if form.validate_on_submit() and form.submit.data:
        # Step 1: get the data
        print("updating a page")
        newtag = form.tag.data
        newtitle = form.title.data
        newtext = form.text.data

        deleteOldPics = form.deleteOldPics.data
        # get pictures at a later step

        # Step 2: find the correct entry in the database
        pagetitle = pagetitle.lower()
        myproject = Project.query.filter_by(tag=pagetitle).first_or_404()

        myproject.tag = newtag
        myproject.title = newtitle
        myproject.text = newtext

        # Check if the user selected whether or not to delete existing pictures
        if deleteOldPics == True:
            # Find all existing pictures in the Image() table
            currentpics = Image.query.filter_by(project_id=myproject.id).all()

            # Delete all of these pictures
            for pic in currentpics:
                # Delete from database
                db.session.delete(pic)

                # Delete the file itself from the database
                imagefilepath = os.path.join(pic_directory, str(pic))
                print("deleting this file:")
                print(imagefilepath)
                if os.path.exists(imagefilepath):
                    os.remove(imagefilepath)

            # The suffix will start from 0 since we deleted everything
            counter = 0

        else:
            # Find the list of pictures in the directory
            currentpics = Image.query.filter_by(project_id=myproject.id).all()

            # Find the number of pictures that are already inside so it can start counting from that
            counter = len(currentpics)

            # In addition, delete the picture for the home page but only IF they added a new one (since there should only be one)

            if form.homepagepicture.data != "":
                # delete from table
                currenthomepagepicture = Image.query.filter_by(
                    project_id=myproject.id, small_for_homepage=True
                ).first()
                if currenthomepagepicture is not None:
                    db.session.delete(currenthomepagepicture)
                    imagefilepath = os.path.join(
                        pic_directory, currenthomepagepicture.filename
                    )
                    os.remove(imagefilepath)

        # Now save these new files to the database
        savePictures(form.pictures.data, myproject.id, counter=counter)

        # save the picture for the home page if they specified it too
        if form.homepagepicture.data is not None:
            savePictures([form.homepagepicture.data], myproject.id, forhomepage=True)

        db.session.commit()
        return redirect(url_for("projects.projectpage", project_name=newtag))

    elif request.method == "GET":
        # look for the thing in the database
        myproject = Project.query.filter_by(tag=pagetitle).first()

        if myproject is None:
            # didn't find anything
            return redirect(url_for("core.home"))

        form.tag.data = myproject.tag
        form.title.data = myproject.title
        form.text.data = myproject.text

    form.setHeader(f"Edit project with URL: /projects/{myproject.tag}")
    return render_template("updatepage.html", form=form, deleteform=deleteform)


# This function is for deleting a page
def deletepage(pagetitle):
    print("Deleting a page")
    project = Project.query.filter_by(tag=pagetitle).first_or_404()
    pictures = Image.query.filter_by(project_id=project.id).all()

    # First, delete the images
    for pic in pictures:
        # Delete from database
        db.session.delete(pic)

        # # Delete the file from the folder
        # imagefilepath = os.path.join(pic_directory, str(pic))
        # # print('deleting this file:')
        # # print(imagefilepath)
        # if os.path.exists(imagefilepath):
        #     os.remove(imagefilepath)

        # Delete from s3
        delete_file_from_s3(pic.filename)


    # Then, delete from the project table
    db.session.delete(project)
    db.session.commit()


def savePictures(picturedata, projectprimarykey, counter=0, forhomepage=False):
    # Check if they uploaded any files
    if picturedata != [""]:
        for file in picturedata:

            # get the extension
            extention = file.filename.split(".")[-1]

            # make the file name

            # just generic picture
            if forhomepage == False:
                filename = str(projectprimarykey) + "_" + str(counter) + "." + extention

            # the small one for the home page
            else:
                filename = str(projectprimarykey) + "_" + "homepage." + extention

            # add the name to the database under the Images table
            # Also it specifies which project it should go with
            newImage = Image(filename, projectprimarykey, forhomepage)
            db.session.add(newImage)

            # Actually save the file to the folder
            # file.save(os.path.join(pic_directory, filename))

            # Save to S3 bucket
            file.filename = filename
            upload_file_to_s3(file)


            counter = counter + 1


@admin_blueprint.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("core.home"))

    form = LoginForm()

    if form.validate_on_submit():
        # check if the username is valid
        username = form.username.data
        password = form.password.data
        user = AdminUser.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            # wrong password/username combo
            return render_template(
                "loginpage.html",
                form=form,
                errormessage="Username and/or password do not match",
            )
        else:
            flash("Logged in")
            login_user(user, remember=True)

            next = request.args.get("next")
            return redirect(next or url_for("core.home"))

    return render_template("loginpage.html", form=form)


@admin_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("core.home"))


@admin_blueprint.app_errorhandler(404)
def error404(e):
    return render_template("404.html"), 404


@admin_blueprint.route("createaccount", methods=["GET", "POST"])
def createaccount():
    form = CreateUserForm()

    if form.validate_on_submit():
        print("test")
        # check that the username is actually valid

        # 1) check if the environment variables are present
        # I'm not sure if this is actually the best way to make sure only I can create an account
        # But it's the only way I could think of

        CREATE_ACC_ID_ENV = os.getenv("CREATE_ACC_ID")
        CREATE_ACC_PW_HASH_ENV = os.getenv("CREATE_ACC_PW_HASH")

        print(CREATE_ACC_ID_ENV)
        print(CREATE_ACC_PW_HASH_ENV)

        if (CREATE_ACC_ID_ENV is None) or (CREATE_ACC_PW_HASH_ENV is None):
            # tell user that they need to set up these variables
            message = "You didn't set up the environment variables"
            print("env variables not set up")
            return render_template("createuser.html", form=form, message=message)
    
        # 2) check that it's actually correct
        if (form.CREATE_ACC_ID.data != CREATE_ACC_ID_ENV) or (check_password_hash(CREATE_ACC_PW_HASH_ENV, form.CREATE_ACC_PW.data) == False):
            # doesn't match
            message = "Incorrect environment variables"
            
            return render_template("createuser.html", form=form, message=message)

        # 3) check that the username doesn't already exist
        
        if AdminUser.query.filter_by(username=form.username.data).first():
            message = "This username already exists"
            return render_template("createuser.html", form=form, message=message)

        # 4) Hash the password and create the user
        # hashing is done by the constructor of the admin user object so I just put in the password directly
        username = form.username.data
        password = form.password.data
        
        newuser = AdminUser(username, password)
        db.session.add(newuser)
        db.session.commit()

        # redirect to home for now
        print("created user")
        return redirect(url_for("core.home"))
    

    
    return render_template("createuser.html", form=form)


@admin_blueprint.route("changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # check if the current password is correct and if the new pws match
        # this is done in the validation on the form
        
        newpasswordhash = generate_password_hash(form.new_password.data)

        # hash it and update the database
        thisuser = AdminUser.query.filter_by(username=current_user.username).first()
        thisuser.password_hash = newpasswordhash
        db.session.commit()
        return redirect(url_for("core.home"))
    return render_template("changepassword.html", form=form)



