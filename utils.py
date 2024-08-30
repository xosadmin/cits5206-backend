import os, configparser
import logging
from datetime import datetime,timedelta
import uuid
import hashlib
import pytz
import random

# Set up logging
logger = logging.getLogger(__name__)

def uuidGen():
    return str(uuid.uuid4())

def getTime(tz):
    tz = pytz.timezone(tz)
    timenow = datetime.now(tz).strftime("%d/%m/%Y-%H:%M:%S")
    return timenow

def CheckIfExpire(dateIssue, expDays, tz_utc):
    date_format = "%d/%m/%Y-%H:%M:%S"
    tz = pytz.timezone(tz_utc)
    dateIssue_dt = datetime.strptime(dateIssue, date_format)
    dateIssue_dt = tz.localize(dateIssue_dt)
    expDate = dateIssue_dt + timedelta(days=int(expDays))
    now_str = getTime(tz_utc)
    now = datetime.strptime(now_str, date_format)
    now = tz.localize(now)
    return now > expDate

def md5Calc(plainText):
    md5 = hashlib.md5()
    md5.update(plainText.encode('utf-8'))
    return str(md5.hexdigest())

def readConf(section, key):
    config_path = "config.ini"
    if not os.path.exists(config_path):
        logger.error(f"Config file {config_path} does not exist")
        raise FileNotFoundError(f"Config file {config_path} does not exist")

    config = configparser.ConfigParser()
    config.read(config_path)
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logger.error(f"Error reading config: {e}")
        raise

def deleteFile(dir,name):
    podcast_path = os.path.join('static', dir, name)
    if os.path.exists(podcast_path):
        os.remove(podcast_path)
        return True
    else:
        return False

def passwordGen():
    symbols = "1234567890abcdefghijklmnopqrstuvwxyz!@#$%^&*()"
    value = ""
    for i in range(0,10):
        value += symbols[random.randint(0,len(symbols)-1)]
    return value
