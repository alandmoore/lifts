"""
These are email-related utilites.

"""
import smtplib
from email.mime.multipart import MIMEMultipart

import sys
if sys.version_info.major > 2:
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders as Encoders
else:
    from email.MIMEText import MIMEText
    from email.MIMEBase import MIMEBase
    from email import Encoders
import platform


def send_email(**kwargs):
    """
    Send an email, optionally with one or more attachments.
    Keyword args are:
    "to" : a single email address, or a list or tuple of email addresses
    "cc" : same as 'to', but these are the cc addresses
    "sender" : sending email
    "subject" : subject line of email
    "message" : the text of the email body
    "attachments" : list of dictionaries for attachments; each dict must have:
        "mimetype" : mimetype of attachment
        "data" : data for attachment
        "filename" : filename for attachment
    """
    recipient = kwargs.get("to", '')
    cc_recipient = kwargs.get("cc", '')
    if type(recipient) in (list, tuple):
        header_recipient = ', '.join(recipient)
    else:
        header_recipient = recipient
        recipient = [x.strip() for x in recipient.split(",")]
    if type(cc_recipient) in (list, tuple):
        header_cc_recipient = ', '.join(cc_recipient)
    else:
        header_cc_recipient = cc_recipient
        cc_recipient = [x.strip() for x in cc_recipient.split(",")]
        
    sender = kwargs.get("sender", "noreply@"+platform.node())
    msg = MIMEMultipart('alternative')
    msg['Subject'] = kwargs.get("subject")
    msg['To'] = header_recipient
    msg['CC'] = header_cc_recipient
    msg['From'] = sender

    message = MIMEText(kwargs.get("message"), 'plain')
    msg.attach(message)

    if kwargs.get('attachments'):
        for attachment in kwargs.get('attachments'):
            mimetype = attachment.get('mimetype', 'text/plain')
            part = MIMEBase(*mimetype.split("/"))
            part.set_payload(attachment.get("data"))
            Encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=attachment.get("filename"))
            msg.attach(part)

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(
        sender,
        recipient + cc_recipient,
        msg.as_string()
    )
    smtp.close()
