from operator import and_
from turtle import update
from flask import jsonify, request
from app import readConf
from models.sqlmodel import db, Users, Tokens, Notes, Snippets, Podcasts, Subscriptions, Library, PodCategory
from actions.extraact import md5Calc, uuidGen, getTime, CheckIfExpire
import logging

logger = logging.getLogger(__name__)

def register_routes(app):
    @app.route("/")
    def index():
        return jsonify({"Status": False, "Detailed Info": "No specified command."})

    @app.route("/login", methods=["POST"])
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
                newToken = Tokens(tokenID=token, userID=query.userID, token=token, dateIssue=getTime(app.config['TIMEZONE']))
                db.session.add(newToken)
                db.session.commit()
                return jsonify({"Status": True, "Token": token}), 201
            else:
                logger.warning(f"Login failed for user {username}")
                return jsonify({"Status": False, "Detailed Info": "Wrong username or password"}), 401
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return jsonify({"Status": False, "Detailed Info": "Internal Server Error"}), 500

    @app.route("/register", methods=["POST"])
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

    @app.route("/changepass", methods=["POST"])
    def changePswd():
        tokenContent = request.form.get('tokenID')
        userID = mapTokenUser(tokenContent)
        password = request.form.get('password')
        if userID and password:
            try:
                md5password = md5Calc(password)
                db.session.execute(update(Users).filter(Users.userID == userID).values(password=md5password))
                db.session.commit()
                return jsonify({"Status": True, "userID": userID})
            except Exception as e:
                logger.error(e)
                return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"})
        else:
            return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})

    @app.route("/addsnippet", methods=["POST"])
    def addSnippet():
        tokenContent = request.form.get('tokenID')
        content = request.form.get('content')
        podid = request.form.get('podid')
        snipID = uuidGen()
        datecreated = getTime(app.config['TIMEZONE'])
        userID = mapTokenUser(tokenContent)
        if userID and content and podid:
            try:
                newSnippet = Snippets(snipID=snipID, userID=userID, podID=podid, snippetContent=content, dateCreated=datecreated)
                db.session.add(newSnippet)
                db.session.commit()
                return jsonify({"Status": True, "SnippetID": snipID})
            except Exception as e:
                logger.error(e)
                return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"})
        else:
            return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})

    @app.route("/addnote", methods=["POST"])
    def doaddnote():
        tokenContent = request.form.get('tokenID')
        content = request.form.get('content')
        podid = request.form.get('podid')
        noteid = uuidGen()
        datecreated = getTime(app.config['TIMEZONE'])
        userID = mapTokenUser(tokenContent)
        if userID and content:
            try:
                newNote = Notes(noteID=noteid, userID=userID, dateCreated=datecreated, content=content, podID=podid)
                db.session.add(newNote)
                db.session.commit()
                return jsonify({"Status": True, "noteID": noteid})
            except Exception as e:
                logger.error(e)
                return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"})
        else:
            return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})

    @app.route("/listnotes", methods=["POST"])
    def get_notes():
        tokenContent = request.form.get('tokenID')
        userID = mapTokenUser(tokenContent)
        if userID:
            query = Notes.query.filter(Notes.userID == userID).all()
            if query:
                result = [
                    {
                        "NoteID": item.noteID,
                        "PodcastID": item.podID,
                        "DateCreated": item.dateCreated
                    }
                    for item in query
                ]
                return jsonify(result)
            else:
                return jsonify({"Result": 0})
        else:
            return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})

    @app.route("/notedetails", methods=["POST"])
    def get_note_details():
        tokenContent = request.form.get('tokenID')
        userID = mapTokenUser(tokenContent)
        noteID = request.form.get('noteID')
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

    @app.route("/search", methods=["POST"])
    def dosearch():
        tokenContent = request.form.get('tokenID')
        userID = mapTokenUser(tokenContent)
        searchQuery = request.form.get('query')
        if userID and searchQuery:
            try:
                podcasts = Podcasts.query.filter(Podcasts.podName.like(f"%{searchQuery}%")).all()
                result = [
                    {
                        "PodcastID": podcast.podID,
                        "PodcastName": podcast.podName,
                        "PodcastURL": podcast.podUrl
                    }
                    for podcast in podcasts
                ]
                return jsonify(result)
            except Exception as e:
                print(e)
                return jsonify({"Status": False, "Detailed Info": "Search failed. Internal Error occurred."})
        else:
            return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})

    @app.route("/listsubscription", methods=["POST"])
    def list_subscriptions():
        tokenContent = request.form.get('tokenID')
        userID = mapTokenUser(tokenContent)
        if userID:
            subscriptions = Subscriptions.query.filter(Subscriptions.userID == userID).all()
            result = [
                {
                    "PodcastID": sub.podID,
                    "SubscriptionDate": sub.subscriptionDate
                }
                for sub in subscriptions
            ]
            return jsonify(result)
        else:
            return jsonify({"Status": False, "Detailed Info": "Unauthenticated"})

    @app.route("/addsubscription", methods=["POST"])
    def add_subscription():
        tokenContent = request.form.get('tokenID')
        userID = mapTokenUser(tokenContent)
        podID = request.form.get('podID')
        if userID and podID:
            try:
                newSubscription = Subscriptions(userID=userID, podID=podID, subscriptionDate=getTime(app.config['TIMEZONE']))
                db.session.add(newSubscription)
                db.session.commit()
                return jsonify({"Status": True})
            except Exception as e:
                print(e)
                return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"})
        else:
            return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})

    @app.route("/addpodcast", methods=["POST"])
    def add_podcast():
        tokenContent = request.form.get('tokenID')
        userID = mapTokenUser(tokenContent)
        podID = uuidGen()
        podName = request.form.get('podName')
        podUrl = request.form.get('podUrl')
        categoryID = request.form.get('categoryID')
        title = request.form.get('title')
        update_date = getTime(app.config['TIMEZONE'])

        if userID and podName and podUrl and categoryID and title:
            try:
                newPodcast = Podcasts(
                    podID=podID,
                    title=title,
                    userID=userID,
                    categoryID=categoryID,
                    podName=podName,
                    podUrl=podUrl,
                    podDuration=0,
                    updateDate=update_date
                )
                db.session.add(newPodcast)
                db.session.commit()
                return jsonify({"Status": True, "PodcastID": podID})
            except Exception as e:
                logger.error(f"Error adding podcast: {e}")
                return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"}), 500
        else:
            return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})



    @app.route("/deletepodcast", methods=["POST"])
    def delete_podcast():
        tokenContent = request.form.get('tokenID')
        userID = mapTokenUser(tokenContent)
        podID = request.form.get('podID')
        if userID and podID:
            try:
                Podcasts.query.filter(Podcasts.podID == podID).delete()
                db.session.commit()
                return jsonify({"Status": True})
            except Exception as e:
                print(e)
                return jsonify({"Status": False, "Detailed Info": "Unknown Internal Error Occurred"})
        else:
            return jsonify({"Status": False, "Detailed Info": "Invalid Parameter(s)"})

    @app.route("/routes")
    def list_routes():
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = f"{rule.endpoint}: {rule.rule} [{methods}]"
            output.append(line)
        return jsonify(routes=output)

    # Helper functions
    def checkIfUserExists(username):
        return Users.query.filter(Users.username == username).first() is not None

    def mapTokenUser(token):
        if not token:
            logger.warning("No token provided")
            return None
        
        query = Tokens.query.filter(Tokens.token == token).first()
        if query:
            if CheckIfExpire(query.dateIssue, int(readConf("systemConfig", "tokenExpireDays")), app.config['TIMEZONE']):
                logger.warning(f"Token {token} expired")
                return None
            return query.userID
        
        logger.warning(f"Token {token} not found")
        return None
