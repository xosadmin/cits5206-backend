import os,sys
import unittest
from app import create_app, db
from models.sqlmodel import Users, Tokens, Notes, Snippets, Podcasts, Subscriptions, Library, PodCategory
from utils import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Ensure the database is clean
        db.drop_all()
        db.create_all()

        # Create a test user
        self.test_user = Users(
            userID=uuidGen(),
            username='testuser',
            password=md5Calc('testpassword'),  # Ensure this matches the password in the login test
            role='user'
        )
        db.session.add(self.test_user)

        # Create a test podcast category
        self.test_category = PodCategory(
            categoryID=uuidGen(),
            categoryName='Test Category'
        )
        db.session.add(self.test_category)

        # Create a test podcast
        self.test_podcast = Podcasts(
            podID=uuidGen(),
            userID=self.test_user.userID,
            categoryID=self.test_category.categoryID,
            podName='Test Podcast',
            title='Test Podcast Title',
            podUrl='http://example.com',
            updateDate=getTime(self.app.config['TIMEZONE'])
        )
        db.session.add(self.test_podcast)
        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Your test cases go here...
    def test_register_user(self):
        response = self.client.post('/register', data=dict(username='newuser', password='newpass'))
        self.assertEqual(response.status_code, 201)
        self.assertIn('userID', response.get_json())

    def test_login_user(self):
        # Attempt to login with correct credentials
        response = self.client.post('/login', data=dict(username='testuser', password='testpassword'))
        self.assertEqual(response.status_code, 201)
        json_data = response.get_json()
        self.assertIn('Token', json_data)
        return json_data['Token']


    def test_add_and_get_notes(self):
        token = self.test_login_user()
        response = self.client.post('/addnote', data=dict(tokenID=token, content='Test Note', podid=self.test_podcast.podID))
        self.assertEqual(response.status_code, 200)
        note_id = response.get_json()['noteID']

        response = self.client.post('/listnotes', data=dict(tokenID=token))
        notes = response.get_json()

        # Debugging prints
        print("Response from /listnotes:", notes)
        print("Expected Note ID:", note_id)

        self.assertIsNotNone(notes, "Notes response is None")
        self.assertTrue(isinstance(notes, list), "Notes response is not a list")
        self.assertTrue(any(note['NoteID'] == note_id for note in notes))

if __name__ == '__main__':
    unittest.main()
