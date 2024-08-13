from flask import *
from sqlalchemy import *
from flask_sqlalchemy import *
from models.sqlmodel import *
from datetime import datetime
import uuid

def uuidGen():
    return str(uuid.uuid4())

sqlInfo = ["127.0.0.1","3306","","",""] # [host,port,username,password,dbname]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+pymysql://' + sqlInfo[2] + ':' + sqlInfo[3] + '@'
                                          + sqlInfo[0] + ':' + sqlInfo[1] + '/' + sqlInfo[4])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = uuidGen()
db = SQLAlchemy(app)

def checkIfUserExists(username):
    query = Users.query.filter(Users.username == username).first()
    if query:
        return True
    else:
        return False

@app.route("/")
def index():
    return jsonify({"Status": "Error", "Detailed Info": "No specified command."})

@app.route("/login", methods=["POST"])
def doLogin():
    username = request.form.get('username')
    password = request.form.get('password')
    query = Users.query.filter(and_(Users.username == username, Users.password == password)).first()
    if query:
        timenow = datetime.now()
        token = uuidGen()
        newToken = Tokens(userID=query.userID, token=token, dateIssue=timenow)
        db.session.add(newToken)
        db.session.commit()
        return jsonify({"Status": True, "Token": token})
    else:
        return jsonify({"Status": "Error", "Detailed Info": "Wrong username or password"})

@app.route("/register", methods=["POST"])
def doRegister():
    username = request.form.get('username')
    password = request.form.get('password')
    userID = uuidGen()
    newUser = Users(userID=userID,username=username,password=password,role="user")
    if not checkIfUserExists(username):
        db.session.add(newUser)
        db.session.commit()
        return jsonify({"Status": True, "userID": userID})
    else:
        return jsonify({"Status": "Error", "Detailed Info": "User already exists!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
