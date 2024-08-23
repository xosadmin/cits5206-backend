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
