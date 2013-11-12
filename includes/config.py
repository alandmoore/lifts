class Config:

    #######################
    # Flask Configuration #
    #######################

    session_key = 'This is not a secure session key'

    ########################
    # Server Configuration #
    ########################

    upload_path = 'uploads/'
    uploads_url = 'http://localhost/files/'
    days_to_keep_files = 30
    
    
    ######################
    # LDAP Configuration #
    ######################

    ldap_config = {
        "host" : None,
        "port" : None,
        "base_dn" : None,
        "bind_dn_username" : None,
        "bind_dn_password" : None,
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

    {note}
    
    """
