import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend_flask.app import create_app
from backend_flask.lib.db import Db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE': ':memory:'  # Use in-memory SQLite for testing
    })
    with app.app_context():
        # Initialize the database
        app.db.setup_tables()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_word(client):
    response = client.post('/api/words', json={
        'kanji': '新しい',
        'romaji': 'atarashii',
        'english': 'new',
        'parts': '新-あたらしい'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'word' in data
    assert data['word']['kanji'] == '新しい'

def test_list_words(client):
    # Create a test word
    client.post('/api/words', json={
        'kanji': '新しい',
        'romaji': 'atarashii',
        'english': 'new',
        'parts': '新-あたらしい'
    })
    
    response = client.get('/api/words')
    assert response.status_code == 200
    data = response.get_json()
    assert 'total' in data
    assert 'words' in data
    assert len(data['words']) > 0

def test_create_group(client):
    response = client.post('/api/groups', json={
        'group_name': 'Study Group A'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert data['name'] == 'Study Group A'

def test_add_word_to_group(client):
    # Create word and group
    word_response = client.post('/api/words', json={
        'kanji': '新しい',
        'romaji': 'atarashii',
        'english': 'new',
        'parts': '新-あたらしい'
    })
    group_response = client.post('/api/groups', json={
        'group_name': 'Study Group A'
    })
    
    word_id = word_response.get_json()['word']['id']
    group_id = group_response.get_json()['id']
    
    response = client.post('/api/word_groups', json={
        'word_id': word_id,
        'group_id': group_id
    })
    assert response.status_code == 201

def test_create_study_session(client):
    # Create group and activity
    group_response = client.post('/api/groups', json={
        'group_name': 'Study Group A'
    })
    activity_response = client.get('/api/study-activities')
    
    group_id = group_response.get_json()['id']
    activity_id = activity_response.get_json()[0]['id']
    
    response = client.post('/api/study_sessions', json={
        'group_id': group_id,
        'study_activity_id': activity_id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert data['group_id'] == group_id

def test_log_review(client):
    # Create word, group, and session
    word_response = client.post('/api/words', json={
        'kanji': '新しい',
        'romaji': 'atarashii',
        'english': 'new',
        'parts': '新-あたらしい'
    })
    group_response = client.post('/api/groups', json={
        'group_name': 'Study Group A'
    })
    session_response = client.post('/api/study_sessions', json={
        'group_id': group_response.get_json()['id'],
        'study_activity_id': 1  # Using default activity ID
    })
    
    word_id = word_response.get_json()['word']['id']
    session_id = session_response.get_json()['id']
    
    response = client.post(f'/api/study_sessions/{session_id}/review', json={
        'word_id': word_id,
        'correct': True
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert data['word_id'] == word_id

def test_list_study_sessions(client):
    # Create some test data
    group_response = client.post('/api/groups', json={
        'group_name': 'Study Group A'
    })
    activity_response = client.get('/api/study-activities')
    
    group_id = group_response.get_json()['id']
    activity_id = activity_response.get_json()[0]['id']
    
    # Create a session
    client.post('/api/study_sessions', json={
        'group_id': group_id,
        'study_activity_id': activity_id
    })
    
    response = client.get('/api/study_sessions')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_reset_study_sessions(client):
    # Create some test data
    group_response = client.post('/api/groups', json={
        'group_name': 'Study Group A'
    })
    activity_response = client.get('/api/study-activities')
    
    group_id = group_response.get_json()['id']
    activity_id = activity_response.get_json()[0]['id']
    
    # Create a session
    session_response = client.post('/api/study_sessions', json={
        'group_id': group_id,
        'study_activity_id': activity_id
    })
    
    session_id = session_response.get_json()['id']
    
    # Reset sessions
    response = client.post('/api/study-sessions/reset')
    assert response.status_code == 200
    
    # Verify sessions are cleared
    sessions = client.get('/api/study_sessions')
    assert len(sessions.get_json()) == 0

def test_get_study_activities(client):
    response = client.get('/api/study-activities')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    for activity in data:
        assert 'id' in activity
        assert 'name' in activity
        assert 'url' in activity