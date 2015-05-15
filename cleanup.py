#!/usr/bin/env python

"""
This script should be run by CRON daily to cleanup expired files.
"""
import os
import datetime
from flask import Flask
import syslog
from includes.logging import Log

# We load flask so we can get the config values the same way flask does
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('includes.config.Config')
app.config.from_pyfile('config.py', silent=True)

log = None

if app.config.get("LOGGING", {}).get("log"):
    log = Log(app.config.get("LOGGING", {}).get("log_path"))


syslog.syslog("LIFTS cleanup starting")

directories = {
    "files": app.config.get("UPLOAD_FOLDER"),
    "passwords": app.config.get("HTPASSWORD_PATH")
}

for key, directory in directories.items():
    if directory[0] != '/':
        directories[key] = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            directory)

max_age = app.config.get("DAYS_TO_KEEP_FILES")

today = datetime.date.today()

for key, directory in directories.items():
    syslog.syslog("Checking {}.".format(key))
    for path, dirlist, filelist in os.walk(directory):
        remove_dir = False
        for filename in filelist:
            ctime_ts = os.stat(os.path.join(path, filename)).st_ctime
            ctime = datetime.date.fromtimestamp(ctime_ts)
            if (today - ctime).days > max_age:
                syslog.syslog("Removing {} from {}".format(filename, path))
                os.remove(os.path.join(path, filename))
                if log:
                    log.log_file_deletion(
                        os.path.join(path, filename)
                    )
                remove_dir = path != directory
        if remove_dir:
            syslog.syslog("Removing {}".format(path))
            os.rmdir(path)

syslog.syslog("LIFTS cleanup finished")
