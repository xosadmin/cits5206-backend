import os
from flask import *
from sqlalchemy import *
from flask_sqlalchemy import *
from models.sqlmodel import *
from actions.extraact import *
from datetime import timedelta
import configparser

def readConf(section,key):
    if os.path.exists("config.ini"):
        config = configparser.ConfigParser()
        config.read("config.ini")
        return str(config[section][key])
    else:
        return None

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+pymysql://' + readConf("database","username") + ':' + readConf("database","password") + '@'
                                          + readConf("database","host") + ':' + readConf("database","port") + '/' + readConf("database","dbname"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = uuidGen()
db.init_app(app)
tz = readConf("systemConfig","timezone")

def checkIfUserExists(username):
    query = Users.query.filter(Users.username == username).first()
    if query:
        return True
    else:
        return False
    
def mapTokenUser(token):
    if token:
        query = Tokens.query.filter(Tokens.token == token).first()
        if query:
            ifExpire = CheckIfExpire(query.dateIssue, int(readConf("systemConfig","tokenExpireDays")))
            if not ifExpire:
                return query.userID
            else:
                return None
        else:
            return None
    else:
        return None

@app.route("/")
def index():
    return jsonify({"Status": False, "Detailed Info": "No specified command."})

@app.route("/login", methods=["POST"])
def doLogin():
    username = request.form.get('username',None)
    password = request.form.get('password',None)
    if username and password:
        md5password = md5Calc(password)
        query = Users.query.filter(and_(Users.username == username, Users.password == md5password)).first()
        if query:
            global tz
            timenow = getTime(tz)
            token = uuidGen()
            newToken = Tokens(tokenID=token, userID=query.userID, token=token, dateIssue=timenow)
            db.session.add(newToken)
            db.session.commit()
            return jsonify({"Status": True, "Token": token})
        else:
            return jsonify({"Status": False, "Detailed Info": "Wrong username or password"})
    else:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})

@app.route("/register", methods=["POST"])
def doRegister():
    username = request.form.get('username',None)
    password = request.form.get('password',None)
    if username and password:
        md5password = md5Calc(password)
        userID = uuidGen()
        newUser = Users(userID=userID,username=username,password=md5password,role="user")
        if not checkIfUserExists(username):
            db.session.add(newUser)
            db.session.commit()
            return jsonify({"Status": True, "userID": userID})
        else:
            return jsonify({"Status": False, "Detailed Info": "User already exists"})
    else:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})
    
@app.route("/changepass", methods=["POST"])
def changePswd():
    tokenContent = request.form.get('tokenID', None)
    userID = mapTokenUser(tokenContent)
    password = request.form.get('password', None)
    if userID and password:
        try:
            md5password = md5Calc(password)
            db.session.execute(Update(Users).filter(Users.userID == userID).values(password = md5password))
            db.session.commit()
            return jsonify({"Status": True, "userID": userID}) 
        except Exception as e:
            print(e)
            return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occured"})

@app.route("/addsnippet", methods=["POST"])
def addSnippet():
    global tz
    tokenContent = request.form.get('tokenID', None)
    content = request.form.get('content', None)
    podid = request.form.get('podid', None)
    snipID = uuidGen()
    datecreated = getTime(tz)
    userID = mapTokenUser(tokenContent)
    if userID and content and podid:
        try:
            newSnippet = Snippets(snipID=snipID,userID=userID,podID=podid,snippetContent=content,dateCreated=datecreated)
            db.session.add(newSnippet)
            db.session.commit()
            return jsonify({"Status": True, "SnippetID": snipID})
        except Exception as e:
            print(e)
            return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occured"})
    else:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})

@app.route("/addnote", methods=["POST"])
def doaddnote():
    global tz
    tokenContent = request.form.get('tokenID', None)
    content = request.form.get('content', None)
    podid = request.form.get('podid', None)
    noteid = uuidGen()
    datecreated = getTime(tz)
    userID = mapTokenUser(tokenContent)
    if userID and tokenContent and content:
        try:
            newNote = Notes(noteID = noteid, userID=userID, dateCreated = datecreated, content = content, podID=podid)
            db.session.add(newNote)
            db.session.commit()
            return jsonify({"Status": True, "noteID": noteid})
        except Exception as e:
            print(e)
            return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occured"})
    else:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})

@app.route("/listnotes", methods=["GET"])
def get_notes():
    tokenContent = request.form.get('tokenID', None)
    userID = mapTokenUser(tokenContent)
    if userID:
        query = Notes.query.filter(Notes.userID == userID).first()
        if query:
            result = {
                "NoteID": query.noteID,
                "PodcastID": query.podID,
                "DateCreated": query.dateCreated
            }
            return jsonify(result)
        else:
            return jsonify({"Result": 0})
    else:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})

@app.route("/getnotedetails", methods=["GET"])
def get_note_details():
    tokenContent = request.form.get('tokenID', None)
    userID = mapTokenUser(tokenContent)
    noteID = request.form.get('noteID', None)
    if userID and noteID:
        query = Notes.query.filter(Notes.noteID == noteID, Notes.userID == userID).first()
        if query:
            result = {
                "NoteID": query.noteID,
                "PodcastID": query.podID,
                "Content": query.content,
                "DateCreated": query.dateCreated
            }
            return jsonify(result)
        else:
            return jsonify({"Result": 0})
    else:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})

@app.route("/search", methods=["GET"])
def dosearch():
    tokenContent = request.form.get('tokenID', None)
    userID = mapTokenUser(tokenContent)
    searchQuery = request.form.get('query', None)
    if userID and searchQuery:
        try:
            podcasts = Podcasts.query.filter(Podcasts.podName.like(f"%{searchQuery}%")).all()
            result = []
            for podcast in podcasts:
                result.append({
                    "PodcastID": podcast.podID,
                    "PodcastName": podcast.podName,
                    "PodcastURL": podcast.podUrl
                })
            return jsonify(result)
        except Exception as e:
            print(e)
            return jsonify({"Status": False, "Detailed Info": "Search failed. Internal Error occurred."})
    else:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})

@app.route("/listsubscription", methods=["POST"])
def list_subscriptions():
    tokenContent = request.form.get('tokenID', None)
    userID = mapTokenUser(tokenContent)
    if userID:
        query = Subscriptions.query.filter(Subscriptions.userID == userID).all()
        if query:
            result = [
                {
                    "SubscriptionID": item.subID,
                    "LibraryID": item.libID,
                    "Date_Of_Subscript": item.dateOfSub
                }
                for item in query
            ]
            return jsonify(result)
        else:
            return jsonify({"Result": 0})
    else:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})

@app.route("/listsnippets", methods=["POST"])
def list_snippets():
    tokenContent = request.form.get('tokenID', None)
    userID = mapTokenUser(tokenContent)
    if userID:
        query = Snippets.query.filter(Snippets.userID == userID).all()
        if query:
            result = [
                {
                    "SnippetID": item.snipID,
                    "PodcastID": item.podID,
                    "Content": item.snippetContent,
                    "dateCreated": item.dateCreated
                }
                for item in query
            ]
            return jsonify(result)
        else:
            return jsonify({"Result": 0})
    else:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})

@app.route("/listpodcasts", methods=["POST"])
def list_podcasts():
    tokenContent = request.form.get('tokenID', None)
    userID = mapTokenUser(tokenContent)
    if userID:
        query = Podcasts.query.all()
        if query:
            result = [
                {
                    "PodcastID": item.podID,
                    "UserID": item.userID,
                    "PodcastName": item.podName,
                    "PodcastURL": item.podUrl
                }
                for item in query
            ]
            return jsonify(result)
        else:
            return jsonify({"Result": 0})
    else:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})

@app.route("/listlibrary", methods=["POST"])
def list_libraries():
    tokenContent = request.form.get('tokenID', None)
    userID = mapTokenUser(tokenContent)
    if userID:
        query = Library.query.filter(Library.userID == userID).all()
        if query:
            result = [
                {
                    "LibraryID": item.libraryID,
                    "LibraryName": item.libraryName
                }
                for item in query
            ]
            return jsonify(result)
        else:
            return jsonify({"Result": 0})
    else:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})

@app.route("/ping")
def responsePing():
    return jsonify({"Status": True, "Detailed Info": "PONG"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

