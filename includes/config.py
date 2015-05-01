class Config:

    #######################
    # Flask Configuration #
    #######################

    SECRET_KEY = 'This is not a secure secret key'
    DEBUG = True

    ##############
    # APPEARANCE #
    ##############

    APP_NAME = "LIFTS"
    SITE_CSS = None
    
    ########################
    # Server Configuration #
    ########################

    # This is a local path to your download directory
    # It needs to be writeable by the user running LIFTS
    UPLOAD_FOLDER = '/tmp/uploads/'

    # This is the outside URL that points the the directory you specified above
    UPLOADS_URL = 'http://localhost/files/'

    # This is a directory where htpasswords will be kept
    # It needs to be writeable by the user running LIFTS, but should not
    # be shared out by any web service
    HTPASSWORD_PATH = 'passwords/'
    DAYS_TO_KEEP_FILES = 30

    HTACCESS_TEMPLATE = """
AuthType  Basic
AuthName  "Password Required"
AuthUserFile  {password_file}
Require valid-user
"""
    
    ######################
    # LDAP Configuration #
    ######################
    AUTH = {
        "auth_backend": "dummy",
        "ldap_config": {
            "host": None,
            "port": None,
            "base_dn": None,
            "bind_dn_username": None,
            "bind_dn_password": None,
            "require_group": None,
            "ssl": None
        }
    }

    #######################
    # Email Configuration #
    #######################
    EMAIL = {
        "email_template":  """
    {user_realname} has just sent you a file using LIFTS.

    The file will be available for download until {expiration_date}
 at the following URL:

    {file_url}

    {password_protection_text}

    {optional_text}
        """,
        "pw_prot_template": """
    The download is password protected.  
Please use the following credentials to access the file:

    username:  {pw_protect_username}
    password:  {pw_protect_password}
    """,

        "opt_text_template": """
    {user_realname} has added the following note:

    {additional_comments}

    """
        }

    #########################
    # Logging configuration #
    #########################

    LOGGING = {
        "log": True,
        "log_path": "/tmp/lifts_log.db"
    }
