#!/usr/bin/env python
"""
LIFTS:  Large Internet File Transfer System
Copyright 2013 Alan D Moore
Published under the GPL v3 license.
Please see README.rst for documentation.
"""

from flask import Flask, g, render_template, \
    request, url_for, redirect, session
from werkzeug import secure_filename
from includes.authenticator import Authenticator, dummy_auth
from includes.ad_auth import AD
from includes.edirectory_auth import EDirectory
from includes.email_utils import send_email
from includes.logging import Log
import uuid
import base64
import os
import datetime
from crypt import crypt
import string
from random import choice

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('includes.config.Config')
app.config.from_pyfile('config.py', silent=True)


@app.before_request
def before_request():
    """Do checks before requests are handled"""

    unsecured_urls = (
        url_for('login_page', _external=True),
        url_for('static', filename='css/style.css', _external=True),
        url_for('static', filename='css/' + (app.config["SITE_CSS"] or ''), _external=True),
        url_for('static', filename='js/jquery.js', _external=True),
        url_for('static', filename='js/lifts.js', _external=True)
    )
    
    # Forward to the login page if not authenticated
    if (
        request.url not in unsecured_urls
        and not session.get("auth")
    ):
        return redirect(url_for("login_page"))

    g.std_args = {
        "app_name": app.config["APP_NAME"],
        "site_css": app.config["SITE_CSS"]
    }
    
    # Make the config globally available
    g.log = (
        app.config["LOGGING"]["log"]
        and Log(app.config["LOGGING"]["log_path"])
        or None
    )

##############
# Main Pages #
##############


@app.route("/")
def index():
    """Return the main page contents."""
    return render_template(
        "main.jinja2",
        username=session['username'],
        user_realname=session['user_realname'],
        user_email=session['user_email'],
        user_specified_credentials=app.config["USER_SPECIFIED_CREDENTIALS"],
        default_username=app.config["DEFAULT_USERNAME"],
        auth_directory_name=app.config["UI"].get("auth_directory_name"),
        techsupport_contact=app.config["UI"].get("techsupport_contact"),
        **g.std_args
    )


@app.route("/send", methods=['POST'])
def file_upload():
    """Process a file submission

    Return a results page.
    """
    # Save the file
    upload = request.files["file_to_send"]
    directory = (base64
                 .urlsafe_b64encode(uuid.uuid4().bytes)
                 .strip(b"=").decode("UTF-8"))
    filename = secure_filename(upload.filename)
    upload_directory = os.path.join(app.config['UPLOAD_FOLDER'], directory)
    os.mkdir(upload_directory)
    upload.save(
        os.path.join(app.config['UPLOAD_FOLDER'], directory, filename)
    )
    file_url = "{}/{}/{}".format(
        app.config["UPLOADS_URL"],
        directory,
        filename
    )

    # Prep some information
    additional_comments = request.form.get("additional_comments").strip()
    pw_protection_text = ""
    optional_text = ""
    password_protection = request.form.get("do_password")
    if additional_comments:
        optional_text = app.config["EMAIL"]["opt_text_template"].format(
            user_realname=session['user_realname'],
            additional_comments=additional_comments
        )

    if password_protection:
        # Generate the Apache HTPasswd file
        if app.config["USER_SPECIFIED_CREDENTIALS"]:
            username = request.form.get("username")
            password = request.form.get("password")
        else:
            username = app.config.get("DEFAULT_USERNAME", "user")
            password = base64.b64encode(os.urandom(6))
        salt = (choice(string.ascii_letters) + choice(string.ascii_letters))
        encrypted_pass = crypt(password, salt)
        password_file = os.path.join(app.config["HTPASSWORD_PATH"],
                                     directory + ".htpw")
        with open(password_file, 'w') as pwfile:
            pwfile.write("{}:{}".format(username, encrypted_pass))
        access_file = os.path.join(upload_directory, ".htaccess")
        with open(access_file, 'w') as acfile:
            acfile.write(app.config["HTACCESS_TEMPLATE"].format(
                password_file=os.path.realpath(password_file)))
        pw_protection_text = app.config["EMAIL"]["pw_prot_template"].format(
            pw_protect_username=username, pw_protect_password=password)

    # Build and send the email
    email_data = {
        "user_realname": session['user_realname'],
        "expiration_date": (
            datetime.date.today() +
            datetime.timedelta(days=app.config["DAYS_TO_KEEP_FILES"])
        ).strftime("%A, %B %d %Y"),
        "file_url": file_url,
        "password_protection_text": pw_protection_text,
        "optional_text": optional_text
    }
    email_text = app.config["EMAIL"]["email_template"].format(**email_data)
    recipients = request.form.getlist("recipients")
    if recipients:
        recipients = [r for r in recipients if r]
    print(recipients)
    subject = "{} shared a file with you".format(session["user_realname"])
    send_email(to=recipients,
               cc=session["user_email"],
               sender=session["user_email"],
               subject=subject, message=email_text)
    # log it
    if g.log:
        g.log.log_post(
            session["username"],
            filename,
            file_url,
            recipients,
            email_text,
            password_protection
        )

    # return results to the user
    return render_template("sent.jinja2", email_text=email_text, **g.std_args)


@app.route("/login", methods=['GET', 'POST'])
def login_page():
    """Display the login page, or process a login attempt."""
    error = None
    username = None
    authenticators = {
        "AD": AD,
        "dummy": dummy_auth,
        "eDirectory": EDirectory
    }
    if request.method == 'POST':
        # attempt to authenticate
        auth = Authenticator(
            authenticators[app.config["AUTH"]["auth_backend"]],
            **app.config["AUTH"]["ldap_config"]
        )
        if auth.check(request.form['username'], request.form['password']):
            session['auth'] = True
            session['username'] = request.form['username']
            session['user_realname'] = auth.get_user_name()
            session['user_email'] = auth.get_user_email()
            g.log.log_login(
                request.form['username'],
                request.remote_addr,
                request.user_agent.string
            )
            return redirect(url_for("index"))
        else:
            username = request.form['username']
            error = "Login Failed"
    return render_template(
        "login.jinja2",
        error=error,
        username=username,
        auth_directory_name=app.config["UI"].get("auth_directory_name"),
        **g.std_args
        )


@app.route("/logout")
def logout():
    """Clear the user's session

    Sends them back to the login page via HTTP redirect.
    """
    session['auth'] = False
    session['username'] = None
    session['user_realname'] = None
    return redirect(url_for("login_page"))


@app.route("/help")
def help():
    """Display a help page"""
    template = app.config["UI"].get("site_help") or "help.jinja2"
    return render_template(
        template,
        techsupport_contact=app.config["UI"].get("techsupport_contact"),
        auth_directory_name=app.config["UI"].get("auth_directory_name"),
        days_to_keep_files=app.config["DAYS_TO_KEEP_FILES"],
        custom_credentials=app.config["USER_SPECIFIED_CREDENTIALS"],
        **g.std_args
    )


@app.route("/history")
def history():
    """Display a user's activity history"""

    history = g.log.get_history(session["username"])

    return render_template(
        "history.jinja2",
        history=history,
        username=session["username"],
        user_realname=session["user_realname"],
        **g.std_args
    )

if __name__ == '__main__':
    app.run()
