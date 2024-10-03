import unittest
import uuid
from app import create_app, db
from models.sqlmodel import Interests, Users, Tokens
from utils import md5Calc, uuidGen, getTime, readConf

class TestCategories(unittest.TestCase):
    def setUp(self):
        # Create Flask application and push context
        self.app = create_app('testing')  # Use the 'testing' configuration
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create Flask test client
        self.client = self.app.test_client()

        # Set the database URI to use SQLite in-memory for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        # Initialize the database
        db.create_all()

        # Create a test user and interests
        self.create_test_user()
        self.create_test_interests()

    def tearDown(self):
        # Roll back and clean up the database after each test
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_user(self):
        """Create a test user and generate a token"""
        self.test_username = "testuser_" + str(uuid.uuid4())[:8]
        self.test_user = Users(
            userID=uuidGen(),
            username=self.test_username,
            password=md5Calc("testpassword"),
            firstname="Test",
            lastname="User",
            dob="1/1/1970"
        )
        db.session.add(self.test_user)
        db.session.commit()

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

    def create_test_interests(self):
        """Create test interests."""
        self.interest_names = ['Technology', 'Business']
        self.interests = {}
        for name in self.interest_names:
            interest_id = uuidGen()
            new_interest = Interests(
                interestID=interest_id,
                interestName=name
            )
            db.session.add(new_interest)
            self.interests[name] = interest_id  # Map name to ID
        db.session.commit()

    def test_list_categories(self):
        """Test listing categories"""
        response = self.client.post('/listcategory', data={'tokenID': self.test_user_token})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_set_user_interest_success(self):
        """Test setting user interest with valid data"""
        interest_ids = ','.join(self.interests.values())
        response = self.client.post('/setuserinterest', data={
            'tokenID': self.test_user_token,
            'userID': self.test_user.userID,
            'interests': interest_ids
        })
        print("Response data:", response.get_json())  # Log response details
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['Status'])

    def test_set_user_interest_invalid_token(self):
        """Test setting user interest with invalid token"""
        interest_ids = ','.join(self.interests.values())
        response = self.client.post('/setuserinterest', data={
            'tokenID': 'invalidtoken',
            'userID': self.test_user.userID,
            'interests': interest_ids
        })
        print("Response data:", response.get_json())  # Log response details
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data['Status'])

    def test_set_user_interest_missing_fields(self):
        """Test setting user interest with missing fields"""
        response = self.client.post('/setuserinterest', data={
            'tokenID': self.test_user_token,
            'interests': ''
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['Status'])

if __name__ == '__main__':
    unittest.main()
