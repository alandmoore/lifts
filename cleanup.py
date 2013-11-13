#!/usr/bin/env python

"""
This script should be run by CRON daily to cleanup expired files.
"""
import os
import datetime
from includes.config import Config
import syslog


syslog.syslog("LIFTS cleanup starting")

files_directory = Config.upload_path
if files_directory[0] != '/':
    files_directory = os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        files_directory)

max_age = Config.days_to_keep_files

today = datetime.date.today()

for path, dirlist, filelist in os.walk(files_directory):
    if path == files_directory:
        continue
    ctime_ts = os.stat(path).st_ctime
    ctime = datetime.date.fromtimestamp(ctime_ts)
    if (today - ctime).days > max_age:
        for filename in filelist:
            syslog("Removing {} from {}".format(filename, path))
            os.remove(os.path.join(path, filename))
        syslog.syslog("Removing {}".format(path))
        os.rmdir(path)

syslog.syslog("LIFTS cleanup finished")
