class Config:

    #######################
    # Flask Configuration #
    #######################

    session_key = 'This is not a secure session key'

    ########################
    # Server Configuration #
    ########################

    # This is a local path to your download directory
    # It needs to be writeable by the user running LIFTS
    upload_path = 'uploads/'

    # This is the outside URL that points the the directory you specified above
    uploads_url = 'http://localhost/files/'

    # This is a directory where htpasswords will be kept
    # It needs to be writeable by the user running LIFTS, but should not
    # be shared out by any web service
    htpassword_path = 'passwords/'
    days_to_keep_files = 30

    htaccess_template = """
AuthType  Basic
AuthName  "Password Required"
AuthUserFile  {password_file}
Require valid-user
"""


    ######################
    # LDAP Configuration #
    ######################
    auth_backend = "dummy"
    ldap_config = {
        "host" : None,
        "port" : None,
        "base_dn" : None,
        "bind_dn_username" : None,
        "bind_dn_password" : None,
        "require_group" : None,
        "ssl" : None
        }


    #######################
    # Email Configuration #
    #######################

    email_template = """
    {user_realname} has just sent you a file using LIFTS.

    The file will be available for download until {expiration_date} at the following URL:

    {file_url}

    {password_protection_text}

    {optional_text}
    """

    password_protected_template = """
    The download is password protected.  Please use the following credentials to access the file:

    username:  {pw_protect_username}
    password:  {pw_protect_password}
    """

    optional_text_template = """
    {user_realname} has added the following note:

    {additional_comments}

    """
