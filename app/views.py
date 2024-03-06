import os
from app import app, db, login_manager, get_upload_images
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm
from werkzeug.security import check_password_hash
from is_safe_url import is_safe_url



###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Joel Plummer")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():

    # Instantiate your form class
    photo = UploadForm()
    # Validate file upload on submit
    if photo.validate_on_submit() and request.method == 'POST':
        # Get file data and save to your uploads folder
        photo = photo.upload.data

        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File Saved', 'success')
        return redirect(url_for('home')) # Update this to redirect the user to a route that displays all uploaded image files
    flash_errors(photo)
    return render_template('upload.html', form=photo) # Update this to redirect the user to a route that displays all uploaded image files



@app.route('/uploads/<filename>')
def get_image(filename):
    rootdir = os.getcwd()
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)

def get_uploaded_images():
    rootdir = os.getcwd()
    lst = []
    for subdir, dirs, files in os.walk(rootdir + '/app/static/uploads'):
        for file in files:
            lst.append(os.path.join(subdir, file).split("\\")[-1])
    return lst[1:]

@app.route('/files')
@login_required
def files():
    images = get_upload_images()
    return render_template('files.html', images=images)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():
        # Get the username and password values from the form.
        username=form.username.data
        password=form.password.data

        # Using your model, query database for a user based on the username
        # and password submitted. Remember you need to compare the password hash.
        # You will need to import the appropriate function to do so.
        # Then store the result of that query to a `user` variable so it can be
        # passed to the login_user() method below.

        user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()

        if user is not None and check_password_hash(user.password, password):  
            # If the user is not blank, meaning if a user was actually found,
            # then login the user and create the user session.
            # user should be an instance of your `User` class
            login_user(user)

                
            # Remember to flash a message to the user
            flash('Logged in successfully.', 'success')    


            return redirect(url_for('upload'))
        else:
            flash('Username or Password is incorrect.', 'danger')
    
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@login_manager.user_loader
def load_user(id):
    login_manager.login_view = 'login'
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
