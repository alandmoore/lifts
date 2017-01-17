#!/usr/bin/env python
# Module for authenticating against Active Directory
# by Alan Moore

try:
    from .ldap_auth import ldap_auth_backend
except SystemError:
    from ldap_auth import ldap_auth_backend


class AD(ldap_auth_backend):

    directory_name = "Microsoft Active Directory"
    user_search_template = "(sAMAccountName={})"
    group_membership_key = "memberOf"
