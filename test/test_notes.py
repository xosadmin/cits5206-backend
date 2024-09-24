import unittest
import uuid
from app import create_app, db
from models.sqlmodel import Notes, PodCategory, Podcasts, Tokens, Users
from utils import getTime, md5Calc, readConf, uuidGen

class TestNotes(unittest.TestCase):
    def setUp(self):
        # Create a Flask application and push the context
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create Flask test client
        self.client = self.app.test_client()

        # Set the database URI with new configuration
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:wsscnha@localhost/cits5206_db'

        # Connect to the database and begin a transaction
        self.connection = db.engine.connect()
        self.transaction = self.connection.begin()

        # Use db.session instead of manually creating scoped session
        self.session = db.session
        self.create_test_user()
        self.create_test_podcast()  # Create the test podcast here


    def tearDown(self):
        # Roll back the transaction to undo any database changes
        self.session.remove()
        self.transaction.rollback()
        self.connection.close()

        # Pop the application context
        self.app_context.pop()

    def create_test_user(self):
        """Create a test user and generate a token"""
        self.test_username = "testuser_" + str(uuid.uuid4())[:8]
        new_user = Users(
            userID=uuidGen(),
            username=self.test_username,
            password=md5Calc("testpassword"),
            firstname="Test",
            lastname="User",
            dob="1/1/1970"
        )
        db.session.add(new_user)
        db.session.commit()

        self.test_user = new_user  # Store the created user for later use

        # Generate a valid token for the test user
        self.test_user_token = uuidGen()
        new_token = Tokens(
            tokenID=uuidGen(),
            userID=self.test_user.userID,
            token=self.test_user_token,
            dateIssue=getTime(readConf("systemConfig", "timezone"))
        )
        db.session.add(new_token)
        db.session.commit()
        
    def create_test_category(self):
        """Create a test category for linking with podcasts."""
        self.test_category_id = uuidGen()  # Generate a unique category ID
        new_category = PodCategory(
            categoryID=self.test_category_id,
            categoryName="Test Category"
        )
        db.session.add(new_category)
        db.session.commit()

    def create_test_podcast(self):
        """Create a test podcast for linking with notes."""
        # Ensure a category is created first
        self.create_test_category()
        
        self.test_podcast_id = uuidGen()
        new_podcast = Podcasts(
            podID=self.test_podcast_id,
            userID=self.test_user.userID,  # Link to the test user
            categoryID=self.test_category_id,  # Use the test category ID
            podName="Test Podcast",
            podUrl="http://example.com/testpodcast.mp3",
            podDuration=120,
            updateDate=getTime(readConf("systemConfig", "timezone"))
        )
        db.session.add(new_podcast)
        db.session.commit()



    def test_add_note_success(self):
        """Test adding a note with valid data."""
        response = self.client.post('/addnote', data={
            'tokenID': self.test_user_token,  # Use the valid token here
            'content': 'This is a test note',
            'podid': self.test_podcast_id  # Use the valid podcast ID
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['Status'])

    def test_add_note_invalid_token(self):
        """Test adding a note with invalid token."""
        response = self.client.post('/addnote', data={
            'tokenID': 'invalidtoken',  # Use an invalid token
            'content': 'This is a test note',
            'podid': self.test_podcast_id  # Use the valid podcast ID
        })
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data['Status'])

