# Module for authenticating against generic LDAP
# by Alan Moore

import ldap3
from .authenticator import auth_backend


class ldap_auth_backend(auth_backend):
    """An authenticator backend for generic ldap"""

    user_search_template = '(uid={})'
    directory_name = "generic LDAP"
    group_membership_key = "memberOf"

    def __init__(
            self,
            host='localhost',
            port=389,
            base_dn="",
            bind_dn_username="",
            bind_dn_password="",
            require_group=None,
            ssl=False,
            **kwargs
    ):
        """Connect to authentication sources and configure basic settings

        Parameters:
          - host: the server hosting the LDAP
          - port: port to connect to. Must be an integer.
          - base_dn: the top-level DN under which to search for users
          - bind_dn_username: a DN to bind to the server for searching
          - bind_dn_password: the password for the bind DN
          - require_group:  A group membership to require for login,
                            or None if any legit account can login.
          - ssl: Whether or not to use ssl.
        """

        self.error = ""
        self.servername = host
        self.base_dn = base_dn
        self.bind_dn = bind_dn_username
        self.bind_pw = bind_dn_password
        self.require_group = require_group
        self.authenticated_user = None
        self.authenticated_dn = None
        self.authsource = self.directory_name + " on " + base_dn

        # attempt to connect to the server
        self.server = ldap3.Server(self.servername, use_ssl=ssl, port=port)
        self.con = ldap3.Connection(
            self.server,
            user=self.bind_dn,
            password=self.bind_pw
        )
        self.bound = self.con.bind()
        if not self.bound:
            self.error = (
                "Could not bind to server {} on port {}."
                .format(self.servername, port)
            )
            if self.bind_dn is not None:
                self.error += "as {}".format(self.bind_dn)
            self.con = False

    def check(self, username=None, password=None):
        """Check the username and password against the auth source

        Return a boolean value
        True if the credentials check out, False if not
        it should also set self.authenticated accordingly
        """
        if not self.con:
            self.error = "No connection to LDAP"
            return False

        if not password:
            self.error = "Invalid credentials: no password supplied"
            return False

        search_succeeded = self.con.search(
            search_base=self.base_dn,
            search_filter=self.user_search_template.format(username),
            search_scope=ldap3.SUBTREE
        )

        if not search_succeeded:
            self.error = "Search for {} failed".format(username)
            return False

        user_dn = self.con.response[0].get("dn")

        if not user_dn:
            self.error = "No such user {}".format(username)
            return False

        try:
            self.con = ldap3.Connection(
                self.server, user=user_dn, password=password
            )
            self.con.bind()
            self.authenticated_user = username
            self.authenticated_dn = user_dn
        except ldap3.LDAPBindError:
            self.error = (
                "Invalid credentials: Login as {} failed."
                .format(username)
            )
            return False

        if not self.con.bound:
            self.error = (
                "Invalid credentials: Login as {} failed."
                .format(username)
            )
            return False

        # If you've gotten to this point, the username/password checks out
        if self.require_group and not (self._in_group(self.require_group)):
            self.error = (
                "Permission denied: not in required group {}"
                .format(self.require_group)
            )
            return False

        return True  # All tests passed!

    def get_auth_user_fullname(self):
        """Return the full name of the authenticated user
        assuming it's available, e.g. from an LDAP or Database table.
        It returns None if there's no authenticated user.
        If there's no name available, it can return the username
        """
        if self.authenticated_user:
            return (
                self._info_on(self.authenticated_user).get("name")
                or self.authenticated_user
            )
        return None

    def get_auth_user_email(self):
        """Return the default email address of the
        authenticated user, assuming it's available from LDAP or something
        Returns None if there's no authenticated user.
        If there's no email available, it returns an empty string
        """
        if self.authenticated_user:
            email = self._info_on(self.authenticated_user).get("mail", [''])
            return email
        return None

    def _in_group(self, group, principle=None):
        if not self.con:
            self.error = "No connection to " + self.directory_name
            return False

        principle = principle or self.authenticated_dn
        group_res = self.con.search(
            self.base_dn,
            "(cn={})".format(group),
            search_scope=ldap3.SUBTREE
        )
        if group_res:
            group_dn = self.con.response[0].get("dn")
            principles_groups = self._info_on_dn(principle).get(
                self.group_membership_key, []
            )

            if group_dn in principles_groups:
                return True
            for g in principles_groups:
                if self._in_group(group, g):
                    return True
        return False

    def _info_on(self, username):
        """Return LDAP information on the given username"""
        if not self.con:
            self.error = "No connection to LDAP."
            return False
        res = self.con.search(
            self.base_dn,
            self.user_search_template.format(username),
            search_scope=ldap3.SUBTREE,
            attributes=ldap3.ALL_ATTRIBUTES
        )

        if not res:
            self.error = "No such user {}".format(username)
            return False
        return self.con.response[0]['attributes']

    def _info_on_dn(self, dn):
        """Return LDAP information on the given DN"""
        if not self.con:
            self.error = "No connection to LDAP."
            return False
        res = self.con.search(
            dn,
            "(objectClass=*)",
            search_scope=ldap3.SUBTREE,
            attributes=ldap3.ALL_ATTRIBUTES
        )
        if not res:
            self.error = "No such DN '{}'".format(dn)
            return {}
        return self.con.response[0]['attributes']
