from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    userID = db.Column(db.String(256), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Tokens(db.Model):
    __tablename__ = 'tokens'
    tokenID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), ForeignKey('users.userID'), nullable=False)
    token = db.Column(db.String(256), unique=True, nullable=False)
    dateIssue = db.Column(db.String(256), nullable=False)

class Notes(db.Model):
    __tablename__ = 'notes'
    noteID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), ForeignKey('users.userID'), nullable=False)
    podID = db.Column(db.String(256), ForeignKey('podcasts.podID'), nullable=False)
    dateCreated = db.Column(db.String(256), nullable=False)
    content = db.Column(db.String(65535), nullable=False)

class Library(db.Model):
    __tablename__ = 'library'
    libraryID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), ForeignKey('users.userID'), nullable=False, default="0")
    libraryName = db.Column(db.String(256), nullable=False)

class Subscriptions(db.Model):
    __tablename__ = "subscriptions"
    subID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), ForeignKey('users.userID'), nullable=False)
    libID = db.Column(db.String(256), ForeignKey('library.libraryID'), nullable=False)
    dateOfSub = db.Column(db.String(256), nullable=False)

class Podcasts(db.Model):
    __tablename__ = "podcasts"
    podID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), ForeignKey('users.userID'), nullable=False)
    podName = db.Column(db.String(256), nullable=False)
    podUrl = db.Column(db.String(512), nullable=False)

class Snippets(db.Model):
    __tablename__ = "snippets"
    snipID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), ForeignKey('users.userID'), nullable=False)
    podID = db.Column(db.String(256), ForeignKey('podcasts.podID'), nullable=False)
    snippetContent = db.Column(db.String(65535), nullable=False)
