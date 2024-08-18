import os
from operator import and_
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import *
from werkzeug.utils import secure_filename
from models.sqlmodel import db, Users, Tokens, Notes, Snippets, Podcasts, Subscriptions, Library, PodCategory
from utils import readConf, md5Calc, uuidGen, getTime, CheckIfExpire, deleteFile
import logging

logger = logging.getLogger(__name__)
mainBluePrint = Blueprint('mainBluePrint', __name__)

def checkIfUserExists(username):
    return Users.query.filter(Users.username == username).first() is not None

def mapTokenUser(token):
    if not token:
        logger.warning("No token provided")
        return None

    query = Tokens.query.filter(Tokens.token == token).first()
    if query:
        if CheckIfExpire(query.dateIssue, int(readConf("systemConfig", "tokenExpireDays")), readConf("systemConfig","timezone")):
            logger.warning(f"Token {token} expired")
            return None
        return query.userID

    logger.warning(f"Token {token} not found")
    return None

def validate_required_fields(data, required_fields):
    """Check if the required fields are present in the data."""
    for field in required_fields:
        if not data.get(field):
            return False, field
    return True, None

@mainBluePrint.route("/")
def index():
    return jsonify({"Status": False, "Detailed Info": "No specified command."})

@mainBluePrint.route("/login", methods=["POST"])
def doLogin():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        logger.warning("Invalid parameters for login")
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    try:
        md5password = md5Calc(password)
        query = Users.query.filter(and_(Users.username == username, Users.password == md5password)).first()
        if query:
            token = uuidGen()
            newToken = Tokens(tokenID=token, userID=query.userID, token=token, dateIssue=getTime(readConf("systemConfig","timezone")))
            db.session.add(newToken)
            db.session.commit()
            return jsonify({"Status": True, "Token": token}), 201
        else:
            logger.warning(f"Login failed for user {username}")
            return jsonify({"Status": False, "Detailed Info": "Wrong username or password"}), 401
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({"Status": False, "Detailed Info": "Internal Server Error"}), 500

@mainBluePrint.route("/register", methods=["POST"])
def doRegister():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    if checkIfUserExists(username):
        return jsonify({"Status": False, "Detailed Info": "User already exists"}), 409

    try:
        newUser = Users(userID=uuidGen(), username=username, password=md5Calc(password), role="user")
        db.session.add(newUser)
        db.session.commit()
        return jsonify({"Status": True, "userID": newUser.userID}), 201
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return jsonify({"Status": False, "Detailed Info": "Internal Server Error"}), 500

@mainBluePrint.route("/changepass", methods=["POST"])
def changePswd():
    tokenContent = request.form.get('tokenID')
    userID = mapTokenUser(tokenContent)
    password = request.form.get('password')
    
    if not userID or not password:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    try:
        md5password = md5Calc(password)
        db.session.execute(update(Users).filter(Users.userID == userID).values(password=md5password))
        db.session.commit()
        return jsonify({"Status": True, "userID": userID})
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/addsnippet", methods=["POST"])
def addSnippet():
    tokenContent = request.form.get('tokenID')
    content = request.form.get('content')
    podid = request.form.get('podid')

    if not tokenContent or not content or not podid:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    userID = mapTokenUser(tokenContent)
    snipID = uuidGen()
    datecreated = getTime(readConf("systemConfig", "timezone"))

    try:
        newSnippet = Snippets(snipID=snipID, userID=userID, podID=podid, snippetContent=content, dateCreated=datecreated)
        db.session.add(newSnippet)
        db.session.commit()
        return jsonify({"Status": True, "SnippetID": snipID})
    except Exception as e:
        logger.error(f"Error adding snippet: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/addnote", methods=["POST"])
def doaddnote():
    tokenContent = request.form.get('tokenID')
    content = request.form.get('content')
    podid = request.form.get('podid')

    if not tokenContent or not content or not podid:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    userID = mapTokenUser(tokenContent)
    noteid = uuidGen()
    datecreated = getTime(readConf("systemConfig", "timezone"))

    try:
        newNote = Notes(noteID=noteid, userID=userID, dateCreated=datecreated, content=content, podID=podid)
        db.session.add(newNote)
        db.session.commit()
        return jsonify({"Status": True, "noteID": noteid})
    except Exception as e:
        logger.error(f"Error adding note: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/listnotes", methods=["POST"])
def get_notes():
    tokenContent = request.form.get('tokenID')
    userID = mapTokenUser(tokenContent)
    if not userID:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"}), 401

    try:
        query = Notes.query.filter(Notes.userID == userID).all()
        result = [{"NoteID": item.noteID, "PodcastID": item.podID, "DateCreated": item.dateCreated} for item in query]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error retrieving notes: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/notedetails", methods=["POST"])
def get_note_details():
    tokenContent = request.form.get('tokenID')
    noteID = request.form.get('noteID')
    userID = mapTokenUser(tokenContent)

    if not userID or not noteID:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    try:
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
    except Exception as e:
        logger.error(f"Error retrieving note details: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/search", methods=["POST"])
def dosearch():
    tokenContent = request.form.get('tokenID')
    searchQuery = request.form.get('query')
    userID = mapTokenUser(tokenContent)

    if not userID or not searchQuery:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    try:
        podcasts = Podcasts.query.filter(Podcasts.podName.like(f"%{searchQuery}%")).all()
        result = [{"PodcastID": podcast.podID, "PodcastName": podcast.podName, "PodcastURL": podcast.podUrl} for podcast in podcasts]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error searching podcasts: {e}")
        return jsonify({"Status": False, "Detailed Info": "Search failed. Internal Error occurred."}), 500

@mainBluePrint.route("/listsubscription", methods=["POST"])
def list_subscriptions():
    tokenContent = request.form.get('tokenID')
    userID = mapTokenUser(tokenContent)
    if userID:
        subscriptions = Subscriptions.query.filter(Subscriptions.userID == userID).all()
        result = [
            {
                "LibraryID": sub.libID,  # Ensure this matches the logic used in the test
                "SubscriptionDate": sub.dateOfSub
            }
            for sub in subscriptions
        ]
        return jsonify(result)
    else:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})


@mainBluePrint.route("/addsubscription", methods=["POST"])
def add_subscription():
    tokenContent = request.form.get('tokenID')
    userID = mapTokenUser(tokenContent)
    libID = request.form.get('libID')
    
    if not userID or not libID:
        logger.error(f"Missing userID or libID: userID={userID}, libID={libID}")
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    try:
        newSubscription = Subscriptions(
            userID=userID,
            libID=libID,
            dateOfSub=getTime(readConf("systemConfig", "timezone"))
        )
        db.session.add(newSubscription)
        db.session.commit()
        return jsonify({"Status": True})
    except Exception as e:
        logger.error(f"Error adding subscription: {e}")
        return jsonify({"Status": False, "Detailed Info": "Internal Server Error"}), 500

@mainBluePrint.route("/listlibrary", methods=["POST"])
def listlibrary():
    tokenContent = request.form.get('tokenID')
    userID = mapTokenUser(tokenContent)

    if not userID:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    try:
        query = Library.query.filter(Library.userID == userID).all()
        result = [{"LibraryID": item.libraryID, "libraryName": item.libraryName} for item in query]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error listing library: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/listcategory", methods=["POST"])
def listcategory():
    tokenContent = request.form.get('tokenID')
    userID = mapTokenUser(tokenContent)

    if not userID:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    try:
        query = PodCategory.query.all()
        result = [{"CategoryID": item.categoryID, "categoryName": item.categoryName} for item in query]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/addpodcast", methods=["POST"])
def add_podcast():
    tokenContent = request.form.get('tokenID')
    podName = request.form.get('podName')
    categoryID = request.form.get('categoryID')
    userID = mapTokenUser(tokenContent)

    if not userID or not podName or not categoryID:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400
    if 'file' not in request.files:
        return jsonify({"Status": False, "Detailed Info": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"Status": False, "Detailed Info": "No selected file"}), 400
    if not file.filename.endswith('.mp3'):
        return jsonify({"Status": False, "Detailed Info": "Invalid file format. Only .mp3 files are allowed."}), 400

    try:
        podID = uuidGen()
        # Secure the filename to prevent directory traversal attacks
        stored_filename = podID + ".mp3"
        upload_path = os.path.join('static', 'podcasts', stored_filename)
        podUrl = readConf("systemConfig","hostname") + "/" + upload_path

        # Save the file to the specified directory
        file.save(upload_path)
        newPodcast = Podcasts(
            podID=podID,
            userID=userID,
            categoryID=categoryID,
            podName=podName,
            podUrl=podUrl,
            podDuration=0,
            updateDate=getTime(readConf("systemConfig", "timezone"))
        )
        db.session.add(newPodcast)
        db.session.commit()
        return jsonify({"Status": True, "PodcastID": newPodcast.podID})
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/deletepodcast", methods=["POST"])
def delete_podcast():
    tokenContent = request.form.get('tokenID')
    podID = request.form.get('podID')
    userID = mapTokenUser(tokenContent)

    if not userID or not podID:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    try:
        Podcasts.query.filter(Podcasts.podID == podID).delete()
        db.session.commit()
        if deleteFile('podcasts', f'{podID}.mp3'):
            return jsonify({"Status": True})
        else:
            return jsonify({"Status": False, "Detailed Info": "The podcast cannot be deleted"}), 400
    except Exception as e:
        logger.error(f"Error deleting podcast: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/deletenote", methods=["POST"])
def delete_podcast():
    tokenContent = request.form.get('tokenID')
    noteID = request.form.get('noteID')
    userID = mapTokenUser(tokenContent)

    if not userID or not noteID:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400
    try:
        Notes.query.filter(Notes.noteID == noteID).delete()
        db.session.commit()
        return jsonify({"Status": True})
    except Exception as e:
        logger.error(f"Error deleting podcast: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/deletesnippet", methods=["POST"])
def delete_podcast():
    tokenContent = request.form.get('tokenID')
    snippetID = request.form.get('snippetID')
    userID = mapTokenUser(tokenContent)

    if not userID or not snippetID:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400
    try:
        Snippets.query.filter(Snippets.snipID == snippetID).delete()
        db.session.commit()
        return jsonify({"Status": True})
    except Exception as e:
        logger.error(f"Error deleting podcast: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/uploadvoicenote", methods=["POST"])
def upload_voice_note():
    tokenContent = request.form.get('tokenID')
    userID = mapTokenUser(tokenContent)
    if userID:
        if 'file' not in request.files:
            return jsonify({"Status": False, "Detailed Info": "No file part in the request"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"Status": False, "Detailed Info": "No selected file"}), 400
        if not file.filename.endswith('.mp3'):
            return jsonify({"Status": False, "Detailed Info": "Invalid file format. Only .mp3 files are allowed."}), 400
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)
        date = getTime(readConf("systemConfig","timezone"))
        stored_filename = filename.split(".")[0] + "_" + userID + "_" + str(date) + ".mp3"
        upload_path = os.path.join('static', 'notes', stored_filename)
        try:
            # Save the file to the specified directory
            file.save(upload_path)
            return jsonify({"Status": True, "Detailed Info": "File successfully uploaded", "filename": filename})
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500
    else:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})


@mainBluePrint.route("/routes")
def list_routes():
    output = []
    for rule in current_app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = f"{rule.endpoint}: {rule.rule} [{methods}]"
        output.append(line)
    return jsonify(routes=output)
