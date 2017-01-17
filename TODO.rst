=================
 LIFTS todo list
=================


Broader Web server support
==========================

LIFTS only really works on Apache right now, because it relies on ``.htaccess`` files to set up password protection.

- Modularize http server backend functions
- Add support for popular servers like **nginx** and **lighttpd**


Master admin control panel
==========================

Some kind of master admin control panel that would allow an admin user to see user logs, file system usage, files uploaded & metadata, etc.
Would need a way to designate admin users (by LDAP group, most likely).

Standalone Backend
==================

Create a db-based standalone backend, so users without an LDAP can still use it.
