import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils import readConf

def readFile(path):
    try:
        with open(path, "r") as r:
            content = r.read()
        return content
    except Exception as e:
        print(e)
        return None
    
def pswdEmailGen(tokenID, username):
    urlHead = readConf("systemConfig", "hostname")
    resetLink = urlHead + "/confirmreset/" + tokenID
    content = f"""
    Dear {username},

    We received a request to reset your password. Please click the link below to reset your password:

    {resetLink}

    If you cannot click on the link above, please copy it and paste on your browser to open.

    Please note that this link will expire in 24 hours. If you did not request a password reset, please ignore this email and your account will remain secure.

    Thank you for using our service!

    Best regards,
    """
    try:
        file_path = os.path.join("templates", f"resetpassword-{tokenID}.html")
        with open(file_path, "w") as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def finalpswdEmailGen(initPassword, username, tokenID):
    content = f"""
    Dear {username},

    Your password has been set to {initPassword}

    Best regards,
    """
    try:
        file_path = os.path.join("templates", f"resetpasswordcomplete-{tokenID}.html")
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "w") as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def sendmail(receiver, subject, contentTempPath):
    sender_email = readConf("mail", "senderMail")
    receiver_email = receiver
    password = readConf("mail", "smtpPassword")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    mailContent = readFile(contentTempPath)
    if mailContent is None:
        print("Cannot find the template")
        return 1

    part = MIMEText(mailContent, "html")
    message.attach(part)

    try:
        smtpServer = readConf("mail", "smtpServer")
        smtpPort = int(readConf("mail", "smtpPort"))
        ifTls = readConf("mail", "useSSL").lower() == "true"

        server = smtplib.SMTP(smtpServer, smtpPort)
        if ifTls:
            server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Mail sent success")
        return 0
    except Exception as e:
        print(f"Cannot send email: {e}")
        return 1
    finally:
        server.quit()
