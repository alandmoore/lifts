#!/usr/bin/env python
# Module for authenticating against eDirectory
# by Alan Moore

import sys
if sys.version_info.major > 2:
    import ldap3 as ldap
else:
    import ldap
from .authenticator import auth_backend

class EDirectory(auth_backend):
    def __init__(self, host='localhost', 
                 port="389", bind_dn="", 
                 bind_pw="", require_group = None, 
                 ssl=False):
        """Contruct an eDirectory connection object.  

        Assumes plaintext LDAP.
        Args:
        host -- The hostname or IP of the directory server
        port -- The port number to connect to
        bind_dn -- A DN (username) to bind to the directory as
        bind_pw -- The bind_dn's password
        require_group -- Require membership in this group for login
        ssl -- Connect using SSL or not
        """
        self.error = ""
        self.host = host
        self.bind_dn = bind_dn
        self.bind_pw = bind_pw
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, False)
        self.authenticated_user = None
        self.authenticated_dn = None
        self.authsource = "Novell eDirectory on " + host
        self.require_group = require_group
        self.ldap_url = ''.join([
            (ssl and "ldaps://") or "ldap://",
            self.host,
            (port and ":{}".format(port)) or ''
        ])
        # attempt to connect to the server
        try:
            self.con = ldap.initialize(self.ldap_url)
            if ssl:
                self.con.start_tls_s()
            self.con.simple_bind_s(self.bind_dn, self.bind_pw)
        except ldap.INVALID_CREDENTIALS:
            self.error = "Could not bind to server {}.".format(self.host)
            if self.bind_dn is not None:
                self.error += "as %s" % self.bind_dn
                self.con = False
        except ldap.SERVER_DOWN:
            self.error = "Could not make connection to {}.".format(self.host)
    def check (self, username, password):
        """Authenticate a user
        
        Return true if the username & password authenticate, otherwise,
        return false;
        """
        if self.con:
            res = self.con.search_s("", ldap.SCOPE_SUBTREE, 
                                    "uid={}".format(username))
        else:
            return False
        # For some stupid reason, ldap will bind successfully 
        # with a valid username and a BLANK PASSWORD, 
        # so we have to disallow blank passwords.
        if not password:
            self.error = ("Invalid credentials: Login as {} failed"
                          .format(username))
            return False

        if not res:
            self.error = "No such user {}".format(username)
            return False
        else:
            dn = res[0][0]
            try:
                self.con.simple_bind_s(dn, password)
                self.authenticated_user = username
                self.authenticated_dn = dn
            except:
                self.error = ("Invalid credentials: Login as {} failed"
                              .format(username))
                return False
        if self.require_group and not (self.in_group(self.require_group)):
            self.error = "Permission Denied"
            return False
        return True

    def info_on(self, username):
        """Return ldap information on the given username"""
        if self.con:
            res = self.con.search_s("", ldap.SCOPE_SUBTREE, 
                                    "uid={}".format(username))
        else:
            return False

        if not res:
            self.error = "No such user {}".format(username)
            return False

        return res[0][1]

    def get_auth_user_fullname(self):
        """Get the full name of the authenticated user from LDAP"""
        if self.authenticated_user:
            info = self.info_on(self.authenticated_user)
            name = "{} {}".format(info.get("givenName", [''])[0], 
                                  info.get("sn", [''])[0])
            return name
        return ""

    def get_auth_user_email(self):
        """Get the email address of the authenticated user from LDAP"""
        if self.authenticated_user:
            info = self.info_on(self.authenticated_user)
            email = info.get("mail", [''])[0]
            return email
        return None

    def in_group(self, group):
        """Check if the authenticated user is in the group
        
        Return true if they are directly in the group.  Indirect
        membership is not determined.
        """
        group_res = self.con.search_s("", ldap.SCOPE_SUBTREE, 
                                      "cn={}".format(group))
        return (group_res and self.authenticated_dn 
                in group_res[0][1].get("member", []))

