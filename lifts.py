#!/usr/bin/env python
"""
LIFTS:  Large Internet File Transfer System
Copyright 2013 Alan D Moore
Published under the GPL v3 license.
Please see README.rst for documentation.
"""

from flask import Flask, g, render_template, request, url_for, redirect, session
from werkzeug import secure_filename
from includes.config import Config
from includes.authenticator import Authenticator, dummy_auth
from includes.ad_auth import AD
from includes.edirectory_auth import EDirectory
from includes.email_utils import send_email
import uuid
import base64
import os
import datetime

app = Flask(__name__)
app.debug = True
app.secret_key = Config().session_key
app.config['UPLOAD_FOLDER'] = Config().upload_path

@app.before_request
def before_request():
    if request.path not in [url_for('login_page'), url_for("static", filename='css/style.css')] and not session.get("auth"):
        return redirect(url_for("login_page"))
    g.config = Config()

##############
# Main Pages #
##############

@app.route("/")
def index():
    return render_template("main.jinja2", username=session['username'], user_realname=session['user_realname'], user_email = session['user_email'])

@app.route("/send", methods=['POST'])
def file_upload():
    #save the file
    upload = request.files["file_to_send"]
    directory = base64.urlsafe_b64encode(uuid.uuid4().bytes).strip("=")
    filename = secure_filename(upload.filename)
    os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], directory))
    upload.save(os.path.join(app.config['UPLOAD_FOLDER'], directory, filename))
    file_url = "{}/{}/{}".format(Config.uploads_url, directory, filename)
    additional_comments = request.form.get("additional_comments").strip()
    password_protection_text = ""
    optional_text = ""
    password_protection = request.form.get("do_password")

    if password_protection:
        password_protection_text = Config.password_protected_template.format({
            "pw_protect_username" : request.form.get("pw_protect_username"),
            "pw_protect_password" : request.form.get("pw_protect_password")
        })

    if additional_comments:
        optional_text = Config.optional_text_template.format(user_realname= session['user_realname'], additional_comments= additional_comments)

    email_data = {
        "user_realname" : session['user_realname'],
        "expiration_date" : (datetime.date.today() + datetime.timedelta(days=Config.days_to_keep_files)).strftime("%A, %B %d %Y"),
         "file_url" : file_url,
         "password_protection_text" : password_protection_text,
         "optional_text" : optional_text
    }

    email_text = Config.email_template.format(**email_data)
    recipients = request.form.get("recipients").split("\n")
    subject = "{} shared a file with you".format(session["user_realname"])
    send_email(to=recipients, cc=session["user_email"], sender=session["user_email"], subject=subject, message= email_text)

    return render_template("sent.jinja2", email_text = email_text)

# Login, Logout
@app.route("/login", methods=['GET', 'POST'])
def login_page():
    error = None
    username = None
    authenticators = {"AD": AD, "dummy": dummy_auth, "eDirectory":EDirectory}
    if request.method == 'POST':
        # attempt to authenticate
        auth = Authenticator(authenticators[Config.auth_backend], **Config.ldap_config)
        if auth.check(request.form['username'], request.form['password']):
            session['auth'] = True
            session['username'] = request.form['username']
            session['user_realname'] = auth.get_user_name()
            session['user_email'] = auth.get_user_email()
            return redirect(url_for("index"))
        else:
            username = request.form['username']
            error = "Login Failed"
    return render_template("login.jinja2", error=error, username=username)

@app.route("/logout")
def logout():
    session['auth'] = False
    session['username'] = None
    session['user_realname'] = None
    return redirect(url_for("login_page"))


if __name__ == '__main__':
    app.run()
