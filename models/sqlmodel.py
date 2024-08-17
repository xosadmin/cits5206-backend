from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    userID = db.Column(db.String(256), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    tokens = db.relationship('Tokens', backref='user', lazy=True)
    notes = db.relationship('Notes', backref='user', lazy=True)
    subscriptions = db.relationship('Subscriptions', backref='user', lazy=True)
    podcasts = db.relationship('Podcasts', backref='user', lazy=True)
    snippets = db.relationship('Snippets', backref='user', lazy=True)


class Tokens(db.Model):
    __tablename__ = 'tokens'
    tokenID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), db.ForeignKey('users.userID'), nullable=False)
    token = db.Column(db.String(256), unique=True, nullable=False)
    dateIssue = db.Column(db.String(256), nullable=False)


class Notes(db.Model):
    __tablename__ = 'notes'
    noteID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), db.ForeignKey('users.userID'), nullable=False)
    podID = db.Column(db.String(256), db.ForeignKey('podcasts.podID'), nullable=False)
    dateCreated = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)


class Library(db.Model):
    __tablename__ = 'library'
    libraryID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), db.ForeignKey('users.userID'), nullable=False)
    libraryName = db.Column(db.String(256), nullable=False)
    subscriptions = db.relationship('Subscriptions', backref='library', lazy=True)


class Subscriptions(db.Model):
    __tablename__ = 'subscriptions'
    subID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), db.ForeignKey('users.userID'), nullable=False)
    libID = db.Column(db.String(256), db.ForeignKey('library.libraryID'), nullable=False)
    dateOfSub = db.Column(db.String(256), nullable=False)


class Podcasts(db.Model):
    __tablename__ = 'podcasts'
    podID = db.Column(db.String(256), primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    userID = db.Column(db.String(256), db.ForeignKey('users.userID'), nullable=False)
    categoryID = db.Column(db.String(256), db.ForeignKey('podCategory.categoryID'), nullable=False)
    podName = db.Column(db.String(256), nullable=False)
    podUrl = db.Column(db.String(512), nullable=False)
    podDuration = db.Column(db.Integer, nullable=False, default=0)
    updateDate = db.Column(db.String(256), nullable=False)
    notes = db.relationship('Notes', backref='podcast', lazy=True)
    snippets = db.relationship('Snippets', backref='podcast', lazy=True)


class Snippets(db.Model):
    __tablename__ = 'snippets'
    snipID = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), db.ForeignKey('users.userID'), nullable=False)
    podID = db.Column(db.String(256), db.ForeignKey('podcasts.podID'), nullable=False)
    snippetContent = db.Column(db.Text, nullable=False)
    dateCreated = db.Column(db.String(256), nullable=False)


class PodCategory(db.Model):
    __tablename__ = 'podCategory'
    categoryID = db.Column(db.String(256), primary_key=True)
    categoryName = db.Column(db.String(256), nullable=False)
    podcasts = db.relationship('Podcasts', backref='category', lazy=True)
