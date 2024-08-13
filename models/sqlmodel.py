from flask_sqlalchemy import *
from sqlalchemy import ForeignKey

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    userID = db.Column(db.String(256), primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Tokens(db.Model):
    __tablename__ = 'tokens'
    tokenID = db.Column(db.String(256), primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, ForeignKey('users.userID'), nullable=False)
    token = db.Column(db.String(256), unique=True, nullable=False)
    dateIssue = db.Column(db.DateTime, nullable=False)
