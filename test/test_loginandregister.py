import unittest
import uuid
from flask import jsonify
from app import create_app, db
from models.sqlmodel import Users, Tokens
from utils import md5Calc, uuidGen

class TestLoginAndRegister(unittest.TestCase):
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

    def tearDown(self):
        # Roll back the transaction to undo any database changes
        self.session.remove()
        self.transaction.rollback()
        self.connection.close()

        # Pop the application context
        self.app_context.pop()

    def create_test_user(self):
        # Generate a unique test username and save it to self.test_username
        self.test_username = "testuser_" + str(uuid.uuid4())[:8]  # Generate a unique username
        new_user = Users(
            userID=uuidGen(),
            username=self.test_username,  # Use the randomly generated username
            password=md5Calc("testpassword"),
            firstname="Test",
            lastname="User",
            dob="1/1/1970"
        )
        db.session.add(new_user)
        db.session.commit()

    def test_login_success(self):
        """Test successful login."""
        # Use the randomly generated username to test successful login
        response = self.client.post('/login', data={'username': self.test_username, 'password': 'testpassword'})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['Status'])
        self.assertIn('Token', data)

    def test_login_failure_invalid_password(self):
        """Test login with an incorrect password."""
        # Test login with the correct username but incorrect password
        response = self.client.post('/login', data={'username': self.test_username, 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data['Status'])

    def test_register_success(self):
        """Test successful user registration."""
        # Generate a new username for the registration test
        new_username = "newuser_" + str(uuid.uuid4())[:8]
        response = self.client.post('/register', data={'username': new_username, 'password': 'newpassword123'})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['Status'])

    def test_register_failure_user_exists(self):
        """Test registration failure when the username already exists."""
        # Attempt to register with an already existing username, should fail
        response = self.client.post('/register', data={'username': self.test_username, 'password': 'password123'})
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertFalse(data['Status'])

    def test_register_failure_long_username(self):
        """Test registration failure when the username is too long."""
        # Test registering with a username that exceeds the allowed length
        long_username = 'a' * 256  # Exceed the maximum username length
        response = self.client.post('/register', data={'username': long_username, 'password': 'password123'})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['Status'])
