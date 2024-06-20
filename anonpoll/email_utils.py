# Import smtplib for the actual sending function
import mimetypes
import os
import smtplib
from email.message import EmailMessage

# from anonpoll.settings import DEBUG, FROM_EMAIL, EMAIL_HOST, DEBUG_EMAIL


class MyTemporaryFile:
    """
    A class representing a temporary file.

    Args:
        file_name (str): The name of the temporary file.
        content: The content of the temporary file.

    Methods:
        get_file_name: Get the name of the temporary file.
        get_content: Get the content of the temporary file.
    """

    def __init__(self, file_name, content):
        self.file_name = file_name
        self.content = content

    def get_file_name(self):
        return self.file_name

    def get_content(self):
        return self.content


def my_send_email(from_email, to_addresses, subject, body, cc_addresses=None, bcc_addresses=None, attachments=None, email_host=None):
    """
    Send an email with HTML body and optional attachments.

    Parameters:
        subject (str): Email subject.
        body (str): HTML body of the email.
        to_addresses (list): List of recipient email addresses.
        cc_addresses (list, optional): List of CC email addresses.
        bcc_addresses (list, optional): List of BCC email addresses.
        attachments (list, optional): List of attachments (file paths or MyTemporaryFile instances).
        from_email (str, optional): Sender email address.
        email_host (str, optional): SMTP server host.
    """

    if cc_addresses is None:
        cc_addresses = []
    if bcc_addresses is None:
        bcc_addresses = []
    if attachments is None:
        attachments = []

    # Create email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_addresses)
    if cc_addresses:
        msg['Cc'] = ', '.join(cc_addresses)

    # Attach body
    msg.set_content("This is a fallback plain text message.")
    msg.add_alternative(body, subtype='html')

    # Attach files
    for attachment in attachments:
        if isinstance(attachment, MyTemporaryFile):
            filename = attachment.get_file_name()
            data = attachment.get_content().encode()
            ctype, _ = mimetypes.guess_type(filename)
        else:
            filename = os.path.basename(attachment)
            ctype, _ = mimetypes.guess_type(attachment)
            with open(attachment, 'rb') as f:
                data = f.read()

        if ctype is None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)

    # Send email
    with smtplib.SMTP(email_host) as s:
        s.send_message(msg, from_addr=from_email, to_addrs=to_addresses + cc_addresses + bcc_addresses)

# Example usage:
# send_email(
#     subject="Your Subject Here",
#     body="<h1>Hello World</h1>",
#     to_addresses=["to@example.com"],
#     cc_addresses=["cc@example.com"],
#     bcc_addresses=["bcc@example.com"],
#     attachments=["/path/to/file.pdf"],
#     from_email="from@example.com",
#     email_host="smtp.example.com"
# )