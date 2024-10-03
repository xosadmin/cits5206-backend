import os
from operator import and_
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import *
from werkzeug.utils import secure_filename
from models.sqlmodel import db, Users, Tokens, Notes, Snippets, Podcasts, Subscriptions, PodCategory, ResetTokens, Interests, UserInterest
from utils import readConf, md5Calc, uuidGen, getTime, CheckIfExpire, deleteFile, passwordGen
from mailsend import sendmail, pswdEmailGen, finalpswdEmailGen
from xml.etree import ElementTree as ET
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
    for field in required_fields:
        if not data.get(field):
            return False, field
    return True, None

@mainBluePrint.route("/")
def index():
    return jsonify({"Status": False, "Detailed Info": "No specified command."})

@mainBluePrint.route("/login", methods=["POST"])
def doLogin():
    username = request.form.get('username', None)
    password = request.form.get('password', None)


    if not username:
        return jsonify({"Status": False, "Detailed Info": "Missing username"}), 400
    if not password:
        return jsonify({"Status": False, "Detailed Info": "Missing password"}), 400

    try:

        md5password = md5Calc(password)
        

        query = Users.query.filter(and_(Users.username == username, Users.password == md5password)).first()
        
        if query:

            token = uuidGen()
            newToken = Tokens(tokenID=token, userID=query.userID, token=token, dateIssue=getTime(readConf("systemConfig", "timezone")))
            db.session.add(newToken)
            db.session.commit()
            
            logger.info(f"User {username} logged in successfully.")
            return jsonify({"Status": True, "Token": token}), 201
        else:
            logger.warning(f"Login attempt failed for user {username}.")
            return jsonify({"Status": False, "Detailed Info": "Invalid username or password"}), 401
    
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({"Status": False, "Detailed Info": "Internal Server Error"}), 500

@mainBluePrint.route("/register", methods=["POST"])
def doRegister():
    username = request.form.get('username', None)
    password = request.form.get('password', None)

    # Define a maximum allowed length for the username
    max_username_length = 255

    if not username or not password:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    # Check if the username exceeds the maximum allowed length
    if len(username) > max_username_length:
        return jsonify({"Status": False, "Detailed Info": "Username is too long"}), 400

    if checkIfUserExists(username):
        return jsonify({"Status": False, "Detailed Info": "User already exists"}), 409

    try:
        newUser = Users(
            userID=uuidGen(),
            username=username,
            password=md5Calc(password),
        )
        db.session.add(newUser)
        db.session.commit()
        return jsonify({"Status": True, "userID": newUser.userID}), 201
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return jsonify({"Status": False, "Detailed Info": "Internal Server Error"}), 500


@mainBluePrint.route("/setuserinfo", methods=["POST"])
def setUserInfo():
    userID = request.form.get('userID',None)
    firstname = request.form.get('firstname',None)
    lastname = request.form.get('lastname',None)
    dob = request.form.get('dob',None)
    if not userID or not firstname or not lastname or not dob:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400
    else:
        query = Update(Users).filter(Users.userID==userID).values(firstname=firstname, lastname=lastname, dob=dob)
        db.session.execute(query)
        db.session.commit()
        return jsonify({"Status": True, "userID": userID})
    
@mainBluePrint.route("/setuserinterest", methods=["POST"])
def setUserInterest():
    tokenContent = request.form.get('tokenID')
    userID = request.form.get('userID')
    interests = request.form.get('interests')

    # Validate that token, userID, and interests are provided
    if not tokenContent or not userID or not interests:
        return jsonify({"Status": False, "Detailed Info": "Missing token, userID, or interests"}), 400

    # Validate the token (using mapTokenUser to validate token)
    if not mapTokenUser(tokenContent):
        return jsonify({"Status": False, "Detailed Info": "Invalid or expired token"}), 401  # Return 401 if token is invalid
    
    # Check if the user exists in the database
    testUser = Users.query.filter(Users.userID == userID).first()
    if not testUser:
        return jsonify({"Status": False, "Detailed Info": "User not found."}), 404

    # Split interests into a list and strip whitespace from each item
    interest_ids = [interest_id.strip() for interest_id in interests.split(",")]
    
    # Fetch all valid interests in one query to optimize database interaction
    valid_interests = Interests.query.filter(Interests.interestID.in_(interest_ids)).all()

    # Check if all provided interests exist in the database
    if len(valid_interests) != len(interest_ids):
        missing_ids = set(interest_ids) - {interest.interestID for interest in valid_interests}
        return jsonify({"Status": False, "Detailed Info": f"Some interest IDs do not exist: {', '.join(missing_ids)}"}), 400

    try:
        # Add user interests to the UserInterest table
        for interest in valid_interests:
            new_user_interest = UserInterest(
                transactionID=uuidGen(),
                userID=userID,
                interestID=interest.interestID
            )
            db.session.add(new_user_interest)

        # Commit the changes to the database
        db.session.commit()
        return jsonify({"Status": True, "Detailed Info": "User interests updated successfully"}), 200

    except Exception as e:
        # Rollback transaction in case of any exception and log the error
        logger.error(f"Error setting user interests: {e}")
        db.session.rollback()
        return jsonify({"Status": False, "Detailed Info": "Internal Server Error"}), 500


@mainBluePrint.route("/changepass", methods=["POST"])
def changePswd():
    tokenContent = request.form.get('tokenID', None)
    password = request.form.get('password', None)
    userID = mapTokenUser(tokenContent)
    
    if not userID:
        logger.warning(f"Invalid token: {tokenContent}")
        return jsonify({"Status": False, "Detailed Info": "Invalid or expired token"}), 401
    
    if not password:
        return jsonify({"Status": False, "Detailed Info": "Missing password"}), 400
    
    try:
        md5password = md5Calc(password)
        db.session.execute(update(Users).filter(Users.userID == userID).values(password=md5password))
        db.session.commit()
        return jsonify({"Status": True, "userID": userID}), 200
    
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/addsnippet", methods=["POST"])
def addSnippet():
    tokenContent = request.form.get('tokenID', None)
    content = request.form.get('content', None)
    podid = request.form.get('podID', None)  # Change from 'podid' to 'podID' for consistency

    # Validate required parameters
    if not tokenContent or not content or not podid:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    # Validate token and map it to a user
    userID = mapTokenUser(tokenContent)
    if not userID:
        return jsonify({"Status": False, "Detailed Info": "Invalid or expired token"}), 401

    # Check if the podcast exists
    podcast = Podcasts.query.filter_by(podID=podid).first()
    if not podcast:
        return jsonify({"Status": False, "Detailed Info": "Podcast not found"}), 404

    snipID = uuidGen()  # Generate a unique snippet ID
    datecreated = getTime(readConf("systemConfig", "timezone"))

    try:
        # Create a new snippet linked to the user and podcast
        newSnippet = Snippets(
            snipID=snipID,
            userID=userID,
            podID=podid,
            snippetContent=content,
            dateCreated=datecreated
        )
        db.session.add(newSnippet)
        db.session.commit()

        return jsonify({"Status": True, "SnippetID": snipID}), 201  # Return 201 for successful creation

    except Exception as e:
        logger.error(f"Error adding snippet: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500


@mainBluePrint.route("/addnote", methods=["POST"])
def doaddnote():
    tokenContent = request.form.get('tokenID', None)
    content = request.form.get('content', None)
    podid = request.form.get('podid', None)

    # Validate if all required parameters are present
    if not tokenContent or not content or not podid:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    # Validate the token and authenticate the user
    userID = mapTokenUser(tokenContent)
    if not userID:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"}), 401  # Invalid or expired token

    # Check if the provided podcast ID exists
    podcast = Podcasts.query.filter_by(podID=podid).first()
    if not podcast:
        return jsonify({"Status": False, "Detailed Info": "Podcast not found"}), 404  # Podcast not found

    # Generate unique note ID and current timestamp
    noteid = uuidGen()
    datecreated = getTime(readConf("systemConfig", "timezone"))

    try:
        # Create and add the new note to the database
        newNote = Notes(noteID=noteid, userID=userID, dateCreated=datecreated, content=content, podID=podid)
        db.session.add(newNote)
        db.session.commit()
        return jsonify({"Status": True, "noteID": noteid}), 201  # Successful note creation
    except Exception as e:
        logger.error(f"Error adding note: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500  # Internal server error


@mainBluePrint.route("/listnotes", methods=["POST"])
def get_notes():
    tokenContent = request.form.get('tokenID',None)
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
    tokenContent = request.form.get('tokenID',None)
    noteID = request.form.get('noteID',None)
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

@mainBluePrint.route("/getsnippets", methods=["POST"])
def getSnippets():
    tokenContent = request.form.get('tokenID', None)
    podid = request.form.get('podID', None)

    # Validate required parameters
    if not tokenContent or not podid:
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

    # Validate token
    userID = mapTokenUser(tokenContent)
    if not userID:
        return jsonify({"Status": False, "Detailed Info": "Invalid or expired token"}), 401

    # Check if the podcast exists
    podcast = Podcasts.query.filter_by(podID=podid).first()
    if not podcast:
        return jsonify({"Status": False, "Detailed Info": "Podcast not found"}), 404

    # Retrieve the snippets for the podcast
    snippets = Snippets.query.filter_by(podID=podid).all()
    result = [{"SnippetID": snip.snipID, "content": snip.snippetContent} for snip in snippets]

    return jsonify({"Status": True, "Snippets": result}), 200


@mainBluePrint.route("/search", methods=["POST"])
def dosearch():
    tokenContent = request.form.get('tokenID',None)
    searchQuery = request.form.get('query',None)
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
    tokenContent = request.form.get('tokenID',None)
    userID = mapTokenUser(tokenContent)
    if userID:
        subscriptions = Subscriptions.query.filter(Subscriptions.userID == userID).all()
        result = [
            {
                "Title": sub.title,
                "rssUrl": sub.rssUrl,
                "Date": sub.dateOfSub
            }
            for sub in subscriptions
        ]
        return jsonify(result)
    else:
        return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})


# @mainBluePrint.route("/addsubscription", methods=["POST"])
# def add_subscription():
#     tokenContent = request.form.get('tokenID',None)
#     userID = mapTokenUser(tokenContent)
#     libID = request.form.get('subscriptionID',None)
    
#     if not userID or not libID:
#         logger.error(f"Missing userID or libID: userID={userID}, libID={libID}")
#         return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

#     try:
#         newSubscription = Subscriptions(
#             userID=userID,
#             libID=libID,
#             dateOfSub=getTime(readConf("systemConfig", "timezone"))
#         )
#         db.session.add(newSubscription)
#         db.session.commit()
#         return jsonify({"Status": True})
#     except Exception as e:
#         logger.error(f"Error adding subscription: {e}")
#         return jsonify({"Status": False, "Detailed Info": "Internal Server Error"}), 500
    
@mainBluePrint.route("/uploadopml", methods=["POST"])
def uploadopml():
    userID = request.form.get('userID')
    if not userID:
        return jsonify({"error": "User ID is required"}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.opml'):
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            nowDate = getTime(tz=readConf("systemConfig","timezone"))

            subscriptions = []

            for outline in root.findall(".//outline"):
                title = outline.get('text')
                rssUrl = outline.get('xmlUrl')
                
                if title and rssUrl:
                    new_subscription = Subscriptions(userID=userID, title=title, rssUrl=rssUrl, dateOfSub=nowDate)
                    db.session.add(new_subscription)
                    subscriptions.append({"title": title, "xmlurl": rssUrl})
            
            db.session.commit()
            return jsonify({"subscriptions": subscriptions}), 200
            
        except ET.ParseError:
            return jsonify({"Status": False, "Detailed Info":  "Invalid OPML format"}), 400
    else:
        return jsonify({"Status": False, "Detailed Info": "Invalid file format. Please upload an OPML file."}), 400

# @mainBluePrint.route("/listlibrary", methods=["POST"])
# def listlibrary():
#     tokenContent = request.form.get('tokenID',None)
#     userID = mapTokenUser(tokenContent)

#     if not userID:
#         return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 400

#     try:
#         query = Library.query.filter(Library.userID == userID).all()
#         result = [{"LibraryID": item.libraryID, "libraryName": item.libraryName} for item in query]
#         return jsonify(result)
#     except Exception as e:
#         logger.error(f"Error listing library: {e}")
#         return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/listcategory", methods=["POST"])
def listcategory():
    tokenContent = request.form.get('tokenID',None)
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
    tokenContent = request.form.get('tokenID',None)
    podName = request.form.get('podName',None)
    categoryID = request.form.get('categoryID',None)
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
        return jsonify({"Status": True, "PodcastID": newPodcast.podID}), 201  # <- Ensure status 201 is returned here
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/deletepodcast", methods=["POST"])
def delete_podcast():
    tokenContent = request.form.get('tokenID', None)
    podID = request.form.get('podID', None)
    userID = mapTokenUser(tokenContent)

    logger.info(f"Delete request received: tokenID={tokenContent}, podID={podID}, userID={userID}")

    if not userID or not podID:
        logger.error("Invalid userID or podID")
        return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"}), 401

    try:
        podcast = Podcasts.query.filter(Podcasts.podID == podID).first()
        if not podcast:
            logger.error(f"Podcast with ID {podID} not found")
            return jsonify({"Status": False, "Detailed Info": "Podcast not found"}), 400

        Podcasts.query.filter(Podcasts.podID == podID).delete()
        db.session.commit()

        if deleteFile('podcasts', f'{podID}.mp3'):
            logger.info(f"Podcast with ID {podID} deleted successfully")
            return jsonify({"Status": True}), 200
        else:
            logger.error("Failed to delete podcast file")
            return jsonify({"Status": False, "Detailed Info": "The podcast file cannot be deleted"}), 400
    except Exception as e:
        logger.error(f"Error deleting podcast: {e}")
        return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500

@mainBluePrint.route("/deletenote", methods=["POST"])
def delete_note():
    tokenContent = request.form.get('tokenID',None)
    noteID = request.form.get('noteID',None)
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
def delete_snippet():
    tokenContent = request.form.get('tokenID',None)
    snippetID = request.form.get('snippetID',None)
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
    tokenContent = request.form.get('tokenID',None)
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
        date = getTime(readConf("systemConfig","timezone"),1)
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

@mainBluePrint.route("/resetpasswordmail", methods=["POST"])
def resetPswdSt1():
    username = request.form.get("username")
    if username:
        query = Users.query.filter(Users.username == username).first()
        if query:
            try:
                userid = query.userID
                token = uuidGen()
                dateCreated = getTime(tz=readConf("systemConfig","timezone"))
                reset_token = ResetTokens(userID=userid, token=token, dateCreated=dateCreated, used=0)
                db.session.add(reset_token)
                db.session.commit()

                pswdEmailGen(token, username)

                # Try sending the email and catch FileNotFoundError if the template doesn't exist
                template_path = f"templates/resetpassword-{token}.html"
                try:
                    sendmail(username, "Password Reset Confirmation", template_path)
                except FileNotFoundError as e:
                    logger.error(f"Error: Template not found for token {token}: {str(e)}")
                    return jsonify({"Status": False, "Detailed Info": f"Template not found at {template_path}"}), 500

                return jsonify({"Status": True, "Detailed Info": "Reset Password Mail Sent"})
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error while sending email: {str(e)}")
                return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500
        else:
            return jsonify({"Status": False, "Detailed Info": "Invalid Username"}), 400
    else:
        return jsonify({"Status": False, "Detailed Info": "Invalid parameter"}), 400


@mainBluePrint.route("/confirmreset/<token>", methods=["GET"])
def resetPswdSt2(token):
    token_record = ResetTokens.query.filter(ResetTokens.token == token).first()
    if token_record:
        if token_record.used == 0:
            user = Users.query.filter(Users.userID == token_record.userID).first()
            if user:
                new_password = passwordGen
                user.password = md5Calc(new_password)
                token_record.used = 1
                try:
                    db.session.commit()
                    finalpswdEmailGen(new_password, user.username, token)
                    sendmail(user.username, "Your password is reset", f"templates/resetpasswordcomplete-{token}.html")
                    return jsonify({"Status": True, "Detailed Info": "Password reset."})
                except Exception as e:
                    db.session.rollback()
                    print(f'Error during reset: {e}')
                    return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500
            else:
                return jsonify({"Status": False, "Detailed Info": "User not found"}), 400
        else:
            return jsonify({"Status": False, "Detailed Info": "Invalid Token"}), 400
    else:
        return jsonify({"Status": False, "Detailed Info": "Invalid Token"}), 400
