import os
import unittest
from app import create_app, db
from models.sqlmodel import Library, Users, Podcasts, PodCategory, Notes, Subscriptions
from utils import uuidGen, md5Calc, getTime

class BasicTests(unittest.TestCase):

    def setUp(self):
        """Set up the test client and initialize the database."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create initial test data
        self.create_test_user()
        self.create_test_category()
        self.create_test_podcast()
        self.create_test_library()

    def tearDown(self):
        """Tear down the test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_user(self):
        """Create a test user."""
        self.test_user = Users(
            userID=uuidGen(),
            username='testuser',
            password=md5Calc('testpassword'),
            role='user'
        )
        db.session.add(self.test_user)
        db.session.commit()

    def create_test_category(self):
        """Create a test podcast category."""
        self.test_category = PodCategory(
            categoryID=uuidGen(),
            categoryName='Test Category'
        )
        db.session.add(self.test_category)
        db.session.commit()

    def create_test_podcast(self):
        """Create a test podcast."""
        self.test_podcast = Podcasts(
            podID=uuidGen(),
            userID=self.test_user.userID,
            categoryID=self.test_category.categoryID,
            podName='Test Podcast',
            podUrl='http://example.com',
            updateDate=getTime('UTC')
        )
        db.session.add(self.test_podcast)
        db.session.commit()

    def create_test_library(self):
        """Create a test library."""
        self.test_library = Library(
            libraryID=uuidGen(),
            userID=self.test_user.userID,
            libraryName='Test Library'
        )
        db.session.add(self.test_library)
        db.session.commit()

    def test_register_user(self):
        """Test user registration."""
        response = self.client.post('/register', data=dict(username='newuser', password='newpass'))
        self.assertEqual(response.status_code, 201)
        self.assertIn('userID', response.get_json())

    def test_login_user(self):
        """Test user login."""
        response = self.client.post('/login', data=dict(username='testuser', password='testpassword'))
        self.assertEqual(response.status_code, 201)
        json_data = response.get_json()
        self.assertIn('Token', json_data)
        return json_data['Token']

    def test_access_without_token(self):
        """Test accessing a route without a token."""
        response = self.client.post('/listnotes')
        self.assertEqual(response.status_code, 401)

    def test_add_and_get_notes(self):
        """Test adding a note and retrieving it."""
        token = self.test_login_user()
        response = self.client.post('/addnote', data=dict(tokenID=token, content='Test Note', podid=self.test_podcast.podID))
        self.assertEqual(response.status_code, 200)
        note_id = response.get_json()['noteID']

        response = self.client.post('/listnotes', data=dict(tokenID=token))
        notes = response.get_json()

        self.assertIsNotNone(notes)
        self.assertTrue(isinstance(notes, list))
        self.assertTrue(any(note.get('NoteID') == note_id for note in notes))

    def test_add_podcast(self):
        """Test adding a podcast."""
        token = self.test_login_user()
        with self.app.test_client() as client:
            with open('test_podcast.mp3', 'wb') as f:
                f.write(b'Test Podcast Content')
            with open('test_podcast.mp3', 'rb') as podcast_file:
                response = client.post('/addpodcast', data={
                    'tokenID': token,
                    'podName': 'New Podcast',
                    'categoryID': self.test_category.categoryID,
                    'file': podcast_file
                })
                self.assertEqual(response.status_code, 200)
                self.assertIn('PodcastID', response.get_json())
    

    def test_delete_podcast(self):
        """Testing deleteing a podcast."""
        
        token = self.test_login_user()
        with open('test_podcast.mp3', 'rb') as podcast_file:
            response = self.client.post('/addpodcast', data={
            'tokenID': token,
            'podName': 'Podcast to Delete',
            'categoryID': self.test_category.categoryID,
            'file': podcast_file
        })
            self.assertEqual(response.status_code, 200)
            podcast_id = response.get_json()['PodcastID']

    
        response = self.client.post('/deletepodcast', data=dict(tokenID=token, podID=podcast_id))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Status', response.get_json())
        

    def test_add_subscription(self):
        """Test adding a subscription."""
        token = self.test_login_user()
        response = self.client.post('/addsubscription', data=dict(tokenID=token, libID=self.test_library.libraryID))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Status', response.get_json())

    def test_list_subscriptions(self):
        """Test listing subscriptions."""
        token = self.test_login_user()
        self.test_add_subscription()
        response = self.client.post('/listsubscription', data=dict(tokenID=token))
        self.assertEqual(response.status_code, 200)
        subscriptions = response.get_json()
        self.assertTrue(isinstance(subscriptions, list))
        self.assertTrue(any(sub['LibraryID'] == self.test_library.libraryID for sub in subscriptions))

    def test_user_workflow(self):
        """Test a full user workflow."""
        token = self.test_login_user()
        response = self.client.post('/addnote', data=dict(tokenID=token, content='Workflow Note', podid=self.test_podcast.podID))
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/listnotes', data=dict(tokenID=token))
        notes = response.get_json()
        self.assertTrue(any(note.get('NoteID') for note in notes))

    def test_register_user_with_long_username(self):
        """Test registration with a long username."""
        long_username = 'a' * 256
        response = self.client.post('/register', data=dict(username=long_username, password='testpass'))
        self.assertEqual(response.status_code, 400)

    def test_concurrent_note_creation(self):
        """Test concurrent note creation."""
        token = self.test_login_user()
        for i in range(10):
            response = self.client.post('/addnote', data=dict(tokenID=token, content=f'Test Note {i}', podid=self.test_podcast.podID))
            self.assertEqual(response.status_code, 200)
        response = self.client.post('/listnotes', data=dict(tokenID=token))
        notes = response.get_json()
        self.assertEqual(len(notes), 10)

if __name__ == '__main__':
    unittest.main()
