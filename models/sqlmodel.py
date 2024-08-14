from sqlalchemy import Column, String, Integer, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    userID = Column(String(256), primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    role = Column(String(50), nullable=False)

class Tokens(Base):
    __tablename__ = 'tokens'
    tokenID = Column(String(256), primary_key=True)
    userID = Column(String(256), ForeignKey('users.userID'), nullable=False)
    token = Column(String(256), unique=True, nullable=False)
    dateIssue = Column(String(256), nullable=False)

class Notes(Base):
    __tablename__ = 'notes'
    noteID = Column(String(256), primary_key=True)
    userID = Column(String(256), ForeignKey('users.userID'), nullable=False)
    podID = Column(String(256), ForeignKey('podcasts.podID'), nullable=False)
    dateCreated = Column(String(256), nullable=False)
    content = Column(String(65535), nullable=False)

class Library(Base):
    __tablename__ = 'library'
    libraryID = Column(String(256), primary_key=True)
    userID = Column(String(256), ForeignKey('users.userID'), nullable=False, default="0")
    libraryName = Column(String(256), nullable=False)

class Subscriptions(Base):
    __tablename__ = "subscriptions"
    subID = Column(String(256), primary_key=True)
    userID = Column(String(256), ForeignKey('users.userID'), nullable=False)
    libID = Column(String(256), ForeignKey('library.libraryID'), nullable=False)
    dateOfSub = Column(String(256), nullable=False)

class Podcasts(Base):
    __tablename__ = "podcasts"
    podID = Column(String(256), primary_key=True)
    userID = Column(String(256), ForeignKey('users.userID'), nullable=False)
    podName = Column(String(256), nullable=False)
    podUrl = Column(String(512), nullable=False)

class Snippets(Base):
    __tablename__ = "snippets"
    snipID = Column(String(256), primary_key=True)
    userID = Column(String(256), ForeignKey('users.userID'), nullable=False)
    podID = Column(String(256), ForeignKey('podcasts.podID'), nullable=False)
    snippetContent = Column(String(65535), nullable=False)
    dateCreated = Column(String(256), nullable=False)
