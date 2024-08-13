from datetime import datetime
import uuid
import hashlib

def uuidGen():
    return str(uuid.uuid4())

def getTime():
    timenow = datetime.now()
    return timenow

def md5Calc(plainText):
    md5 = hashlib.md5()
    md5.update(plainText.encode('utf-8'))
    return str(md5.hexdigest())
