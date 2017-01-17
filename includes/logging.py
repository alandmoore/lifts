"""
Logging support for LIFTS.

This implements a log to a SQLITE database.
"""

import sqlite3 as sqlite

TABLES = {
    "post_log": """CREATE TABLE post_log (
    id INTEGER PRIMARY KEY
    ,posted_on  DATETIME DEFAULT CURRENT_TIMESTAMP
    ,posted_by  TEXT
    ,filename   TEXT
    ,path       TEXT
    ,url        TEXT
    ,recipients TEXT
    ,comments    TEXT
    ,protected  BOOLEAN
    ,on_server  BOOLEAN DEFAULT 1
    )
    """,
    "auth_log": """CREATE TABLE auth_log (
    id INTEGER PRIMARY KEY
    ,login_time  DATETIME DEFAULT CURRENT_TIMESTAMP
    ,user_id TEXT
    ,ip_address TEXT
    ,user_agent TEXT
    )"""
}


def dict_factory(cursor, row):
    d = {}
    for i, column in enumerate(cursor.description):
        colname = column[0]
        d[colname] = row[i]
    return d


class Log(object):
    """The Log object for LIFTS

    This is an interface to a SQLite database that will store our log.
    """

    def __init__(self, filename):
        """Connect to the logging database file; create if necessary"""
        try:
            self.db = sqlite.connect(filename)
        except sqlite.OperationalError as e:
            print("Unable to open {} for logging.".format(filename))
            raise e
        else:
            self.db.row_factory = dict_factory

        self.cursor = self.db.cursor()
        # Test if the tables exists, create if not
        query = """
        SELECT :tablename IN
        (SELECT name FROM sqlite_master WHERE type='table') AS table_exists"""
        for table in TABLES.keys():
            self.cursor.execute(query, {"tablename": table})
            exists = self.cursor.fetchone()["table_exists"]
            if not exists:
                self.cursor.execute(TABLES[table])

    def log_post(
            self, posted_by, filename, path,
            url, recipients, comments, protected
    ):
        query_data = {
            "posted_by": posted_by,
            "filename": filename,
            "path": path,
            "url": url,
            "recipients": ', '.join(x.strip() for x in recipients),
            "comments": comments,
            "protected": protected
        }
        query = """INSERT INTO post_log
        (posted_by, filename, path, url, recipients, comments, protected)
        VALUES (:posted_by, :filename, :path, :url, :recipients,
        :comments, :protected)
        """
        self.cursor.execute(query, query_data)
        self.db.commit()

    def log_login(self, uid, ip, user_agent):
        query_data = {
            "user_id": uid,
            "ip_address": ip,
            "user_agent": user_agent
        }
        query = """INSERT INTO auth_log
        (user_id, ip_address, user_agent)
        VALUES (:user_id, :ip_address, :user_agent)
        """
        self.cursor.execute(query, query_data)
        self.db.commit()

    def get_history(self, uid):
        """Retrieve a user's activity history."""

        data = {}
        login_query = """SELECT * FROM auth_log WHERE user_id=:user_id ORDER BY login_time DESC"""
        send_query = """SELECT * FROM post_log WHERE posted_by=:user_id ORDER BY posted_on DESC"""
        query_data = {"user_id": uid}
        self.cursor.execute(login_query, query_data)
        data["logins"] = self.cursor.fetchall()
        self.cursor.execute(send_query, query_data)
        data["sent"] = self.cursor.fetchall()

        return data

    def log_file_deletion(self, path):
        """Called when a file is deleted, to record that it's gone"""

        query = """UPDATE post_log SET on_server=0 WHERE path=:path"""
        self.cursor.execute(query, {"path": path})
        self.db.commit()
        
