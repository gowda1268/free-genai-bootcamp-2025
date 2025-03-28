import pytest
from backend_flask.app import create_app  # Adjusted import statement

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_create_study_session(client):
    response = client.post('/api/study_sessions', json={'group_id': 1, 'study_activity_id': 2})
    assert response.status_code == 201
    assert b'Study session created successfully' in response.data

def test_log_review(client):
    response = client.post('/api/study_sessions/1/review', json={'word_id': 5, 'correct': 1})
    assert response.status_code == 201
    assert b'Review logged successfully' in response.data

def test_reset_study_sessions(client):
    response = client.post('/api/study-sessions/reset')
    assert response.status_code == 200
    assert b'Study history cleared successfully' in response.data

def test_get_words(client):
    response = client.get('/api/words')
    assert response.status_code == 200

def test_create_word(client):
    response = client.post('/api/words', json={'word': '新しい'})
    assert response.status_code == 201
    assert b'Word created successfully' in response.data

def test_get_groups(client):
    response = client.get('/api/groups')
    assert response.status_code == 200

def test_create_group(client):
    response = client.post('/api/groups', json={'group_name': 'Study Group A'})
    assert response.status_code == 201
    assert b'Group created successfully' in response.data

def test_get_recent_session(client):
    response = client.get('/dashboard/recent-session')
    assert response.status_code == 200

def test_get_study_activities(client):
    response = client.get('/api/study-activities')
    assert response.status_code == 200