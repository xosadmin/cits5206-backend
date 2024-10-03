import unittest
import uuid
from app import create_app, db
from models.sqlmodel import Users, Tokens, Subscriptions
from utils import md5Calc, uuidGen, getTime, readConf

class TestSubscriptions(unittest.TestCase):
    def setUp(self):
        # Create a Flask application and push context
        self.app = create_app('testing')  # Ensure 'testing' uses SQLite in-memory
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Set the database to use SQLite in-memory for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize the database
        db.create_all()

        # Initialize the test client
        self.client = self.app.test_client()

        # Create test data
        self.create_test_user()
        self.create_test_subscription()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
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

    def create_test_subscription(self):
        """Create a test subscription for the user."""
        new_subscription = Subscriptions(
            userID=self.test_user.userID,
            title="Test Subscription",
            rssUrl="http://example.com/rss",
            dateOfSub=getTime(readConf("systemConfig", "timezone"))
        )
        db.session.add(new_subscription)
        db.session.commit()

    def test_list_subscriptions_success(self):
        """Test listing subscriptions with a valid token."""
        response = self.client.post('/listsubscription', data={
            'tokenID': self.test_user_token  # Use the valid token here
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]['Title'], 'Test Subscription')
        self.assertEqual(data[0]['rssUrl'], 'http://example.com/rss')

    def test_list_subscriptions_invalid_token(self):
        """Test listing subscriptions with an invalid token."""
        response = self.client.post('/listsubscription', data={
            'tokenID': 'invalidtoken'  # Invalid token
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['Status'])
        self.assertIn('Detailed Info', data)

if __name__ == '__main__':
    unittest.main()
