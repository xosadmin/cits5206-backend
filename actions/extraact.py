from datetime import datetime,timedelta
import uuid
import hashlib
import pytz

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
