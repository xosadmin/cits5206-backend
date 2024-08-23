import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils import readConf

def readFile(path):
    try:
        r = open(path, "r")
        content = r.readlines()
        r.close()
        return content
    except Exception as e:
        print(e)
        return None

def sendmail(receiver,subject,contentTempPath):
    sender_email = readConf("mail","senderMail")
    receiver_email = receiver
    password = readConf("mail","smtpPassword")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    mailContent = readFile(contentTempPath)
    part = MIMEText(mailContent, "html")
    message.attach(part)

    try:
        smtpServer = readConf("mail","smtpServer")
        smtpPort = int(readConf("mail","smtpPort"))
        server = smtplib.SMTP(smtpServer, smtpPort)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        return 0
    except Exception as e:
        print(e)
        return 1
    finally:
        server.quit()
