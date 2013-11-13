#!/usr/bin/env python
# Module for authenticating against eDirectory
# by Alan Moore

import ldap
from .authenticator import auth_backend

class EDirectory(auth_backend):
    def __init__(self, host='localhost', port="389", bind_dn="", bind_pw="", require_group = None, ssl=False):
        """Contructor for the connection.  Assumes plaintext LDAP"""
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
        #attempt to connect to the server
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
        """Given a simple username and password, return true or false if the user is authenticated"""
        if self.con:
            res = self.con.search_s("", ldap.SCOPE_SUBTREE, "uid=%s" % username)
        else:
            return False
        #For some stupid reason, ldap will bind successfully with a valid username and a BLANK PASSWORD, so we have to disallow blank passwords.
        if not password:
            self.error = "Invalid credentials: Login as %s failed" % username
            return False

        if not res:
            self.error = "No such user %s" % username
            return False
        else:
            dn = res[0][0]
            #print (dn)
            try:
                self.con.simple_bind_s(dn, password)
                self.authenticated_user = username
                self.authenticated_dn = dn
            except:
                self.error = "Invalid credentials: Login as %s failed" % username
                return False
        if self.require_group and not (self.in_group(self.require_group)):
            self.error = "Permission Denied"
            return False
        return True

    def info_on(self, username):
        """Returns ldap information on the given username"""
        if self.con:
            res = self.con.search_s("", ldap.SCOPE_SUBTREE, "uid=%s" % username)
        else:
            return False

        if not res:
            self.error = "No such user %s" % username
            return False

        return res[0][1]

    def get_auth_user_fullname(self):
        if self.authenticated_user:
            info = self.info_on(self.authenticated_user)
            name = "{} {}".format(info.get("givenName", [''])[0], info.get("sn", [''])[0])
            return name
        return ""

    def get_auth_user_email(self):
        if self.authenticated_user:
            info = self.info_on(self.authenticated_user)
            email = info.get("mail", [''])[0]
            return email
        return None

    def in_group(self, group):
        group_res = self.con.search_s("", ldap.SCOPE_SUBTREE, "cn={}".format(group))
        if group_res and self.authenticated_dn in group_res[0][1].get("member", []):
            return True
        return False
