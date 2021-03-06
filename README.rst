============================================
 LIFTS: Large Internet File Transfer System
============================================

What is LIFTS?
==============

People in organizations often need to send large files both inside and outside the organization.  Their go-to technology for this is often, unfortunately, e-mail attachments.  This creates a raft of problems, especially in environments where e-mail has to be logged.  The alternative is usually something like FTP or CMS software, which requires setting up accounts and other overhead that's too big a pain for a one-off file transfer.

Enter LIFTS.  LIFTS allows users to log in to a simple web interface, upload the file, and easily send a download URL to the intended recipients.

How does it work?
=================

LIFTS users login using their LDAP (Active Directory, e.g.) credentials.

They specifiy a file they want to share, and one or more recipient email addresses.  They can optionally specify a username and password to secure the download directory, and add additional comments.  Then they click "send".

LIFTS copies the file to a unique folder in a location you specify on your web server, and then sends emails to the recipients specifying the download URL, authentication details, and any additional comments.

Requirements
============

- Python 2.7+ or Python 3.4+
- LIFTS is based on Flask, and requires ``flask``.  It is probably best to run it using a python virtual environment.
- LIFTS needs to authenticate with an LDAP service, such as Active Directory or eDirectory.  It also requires the ``ldap3`` library.
- You probably want to run it using a real web server, such as apache with mod_wsgi.
- You should almost certainly run it on a unixlike system such as Linux or BSD where there is a decent cron daemon and GNU find.
- You also need to run it on a server where some sort of MTA is running and properly configured (a.k.a. ``sendmail`` functionality).
- Finally, you need a directory on that server being shared publicly by apache, where the uploaded files will go.

Example Setup
=============

- Install your favorite GNU/Linux distro with python, python-virtualenv, python-pip, apache2, and apache2_mod_wsgi
- Add a system user called "lifts"
- Configure apache's webroot to `/srv/www/htdocs`
- Clone LIFTS into `/srv/www/lifts`
- Create a virtualenv in `/srv/www/lifts/env`::

   cd /srv/www/lifts
   virtualenv env
   source env/bin/activate
   pip install -r requirements.txt
   deactivate

- Create the directories `/srv/www/htdocs/files` and `/srv/www/passwords` and give "lifts" full r/w permissions
- Add a site to your Apache config like this::

    WSGIScriptAlias /lifts /srv/www/lifts/lifts.wsgi
    WSGIDaemonProcess lifts user=lifts group=users python-path=/srv/www/lifts

    # For Apache 2.2
    <Directory /srv/www/lifts>
        Order deny,allow
        Allow from all
    </Directory>

    # Or for Apache 2.4 +
    <Directory /srv/www/lifts>
        Require all granted
    </Directory>



- Create an instance-specific config at `/srv/www/lifts/instance/config.py`, for example::

    APP_NAME = "My Company's LIFTS"
    SECRET_KEY = "Some really long random string of characters"
    AUTH = {
      "auth_backend": "AD",
      "ldap_config": {
        "host": "my.domain.controller.mydomain.local",
        "base_dn": "dc=mydomain, dc=local",
        "bind_dn_username": "mybinduser@mydomain.local",
        "bind_dn_password": "mybindusers_password",
        "require_group": None,
        "ssl": True
      }
    }
    UPLOAD_FOLDER = "/srv/www/htdocs/files"
    HTPASSWORD_PATH = "/srv/www/passwords"
    UI = {
      "techsupport_contact": "How to contact your IT dept",
      "auth_directory_name": "Active Directory at MyDomain.local",
      "site_help": None
    }

- Create a crontab job for either root or lifts to run `cd /srv/htdocs/lifts && env/bin/python cleanup.py` daily

- Restart apache and check it out!

Status
======

LIFTS is in beta at my organization.  It's obviously a bit tricky to get set up if you're not an experienced Linux admin.
If you are using LIFTS in production, please take care when merging the latest changes, as things are still subject to change.

Contributing
============

Yes, please do!

See TODO.rst for ideas on what you might add.


License
=======

LIFTS is published under the GPL v3.
For details see the COPYING file included.
