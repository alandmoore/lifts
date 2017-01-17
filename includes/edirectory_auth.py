#!/usr/bin/env python
# Module for authenticating against eDirectory
# by Alan Moore

try:
    from .ldap_auth import ldap_auth_backend
except SystemError:
    from ldap_auth import ldap_auth_backend


class EDirectory(ldap_auth_backend):
    directory_name = "Novell eDirectory"
    user_search_template = "(uid={})"
    group_membership_key = 'groupMembership'
