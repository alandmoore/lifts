#!/usr/bin/env python

"""
This script should be run by CRON daily to cleanup expired files.
"""
import os
import datetime
from includes.config import Config
import syslog


syslog.syslog("LIFTS cleanup starting")

directories = {"files" : Config.upload_path, "passwords" :Config.htpassword_path}

for key, directory in directories.items():
    if directory[0] != '/':
        directories[key] = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            directory)

max_age = Config.days_to_keep_files

today = datetime.date.today()

for key, directory in directories.items():
    syslog.syslog("Checking {}.".format(key))
    for path, dirlist, filelist in os.walk(directory):
        remove_dir = False
        for filename in filelist:
            ctime_ts = os.stat(os.path.join(path, filename)).st_ctime
            ctime = datetime.date.fromtimestamp(ctime_ts)
            if (today - ctime).days > max_age:
                syslog("Removing {} from {}".format(filename, path))
                os.remove(os.path.join(path, filename))
                remove_dir = path != directory
        if remove_dir:
            syslog.syslog("Removing {}".format(path))
            os.rmdir(path)

syslog.syslog("LIFTS cleanup finished")
