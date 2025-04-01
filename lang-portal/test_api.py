import requests
import json
import time
import pytest

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="session")
def flask_server():
    """Start the Flask server before tests"""
    import subprocess
    import time
    
    # Start the Flask server in a subprocess
    server_process = subprocess.Popen(['python', '-m', 'flask', 'run', '--port', '5000'])
    
    # Wait for the server to start
    time.sleep(2)
    
    yield
    
    # Clean up after tests
    server_process.terminate()
    server_process.wait()

@pytest.fixture(scope="session")
def word_id(flask_server):
    """Create a test word and return its ID"""
    word_data = {
        "kanji": "新しい",
        "romaji": "atarashii",
        "english": "new",
        "parts": "形容詞"
    }
    response = requests.post(f"{BASE_URL}/api/words", json=word_data)
    assert response.status_code == 201
    word = response.json()['word']
    return word['id']

@pytest.fixture(scope="session")
def group_id(flask_server):
    """Create a test group and return its ID"""
    group_data = {
        "group_name": "Adjectives"
    }
    response = requests.post(f"{BASE_URL}/api/groups", json=group_data)
    assert response.status_code == 201
    group = response.json()
    return group['id']

@pytest.fixture(scope="session")
def study_activity_id(flask_server):
    """Create a test study activity and return its ID"""
    activity_data = {
        "name": "Flashcards",
        "url": "https://example.com/flashcards",
        "preview_url": "https://example.com/flashcards/preview"
    }
    response = requests.post(f"{BASE_URL}/api/study-activities", json=activity_data)
    assert response.status_code == 201
    activity = response.json()
    return activity['id']

@pytest.mark.usefixtures("flask_server")
def test_words():
    print("\nTesting Words API...")
    
    # Create a new word
    word_data = {
        "kanji": "新しい",
        "romaji": "atarashii",
        "english": "new",
        "parts": "形容詞"
    }
    print(f"Creating word with data: {word_data}")
    response = requests.post(f"{BASE_URL}/api/words", json=word_data)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    assert response.status_code == 201
    response_data = response.json()
    print(f"Response data: {response_data}")
    assert 'word' in response_data
    word = response_data['word']
    assert 'id' in word
    word_id = word['id']
    print(f"Created word with id: {word_id}")
    print("✅ Word created successfully")
    
    # Get all words
    response = requests.get(f"{BASE_URL}/api/words")
    print(f"Get all words status code: {response.status_code}")
    print(f"Get all words content: {response.text}")
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, dict)
    assert 'words' in response_data
    assert isinstance(response_data['words'], list)
    assert len(response_data['words']) > 0
    print(f"Found {len(response_data['words'])} words")
    print("✅ Words retrieved successfully")
    
    # Get the specific word we just created
    response = requests.get(f"{BASE_URL}/api/words/{word_id}")
    print(f"Get specific word status code: {response.status_code}")
    print(f"Get specific word content: {response.text}")
    assert response.status_code == 200
    word = response.json()
    assert isinstance(word, dict)
    assert 'id' in word
    assert word['kanji'] == "新しい"
    print("✅ Specific word retrieved successfully")

@pytest.mark.usefixtures("flask_server")
def test_groups():
    print("\nTesting Groups API...")
    
    # Test validation - missing name
    invalid_data = {}
    response = requests.post(f"{BASE_URL}/api/groups", json=invalid_data)
    assert response.status_code == 400
    assert "group_name is required" in response.json()['error']
    print("✅ Validation test passed - missing name")
    
    # Test validation - invalid name type
    invalid_data = {"group_name": 123}
    response = requests.post(f"{BASE_URL}/api/groups", json=invalid_data)
    assert response.status_code == 400
    assert "must be a string" in response.json()['error']
    print("✅ Validation test passed - invalid name type")
    
    # Create a new group
    group_data = {
        "group_name": "Adjectives"
    }
    response = requests.post(f"{BASE_URL}/api/groups", json=group_data)
    assert response.status_code == 201
    group = response.json()
    group_id = group['id']
    print("✅ Group created successfully")
    
    # Get all groups
    response = requests.get(f"{BASE_URL}/api/groups")
    assert response.status_code == 200
    groups = response.json()
    assert len(groups) > 0
    print("✅ Groups retrieved successfully")
    
    # Get specific group
    response = requests.get(f"{BASE_URL}/api/groups/{group_id}")
    assert response.status_code == 200
    group = response.json()
    assert 'name' in group
    assert group['name'] == "Adjectives"
    print("✅ Get specific group test passed")
    
    # Update group
    update_data = {
        "group_name": "Adjectives Updated"
    }
    response = requests.put(f"{BASE_URL}/api/groups/{group_id}", json=update_data)
    assert response.status_code == 200
    print("✅ Group update test passed")

@pytest.mark.usefixtures("flask_server", "word_id", "group_id")
def test_word_groups(word_id, group_id):
    print("\nTesting Word-Group Relationship...")
    
    # Create word-group relationship
    relationship_data = {
        "word_id": word_id,
        "group_id": group_id
    }
    response = requests.post(f"{BASE_URL}/api/word_groups", json=relationship_data)
    assert response.status_code == 201
    print("✅ Word-Group relationship created successfully")
    
    # Get word's groups
    response = requests.get(f"{BASE_URL}/api/words/{word_id}/groups")
    assert response.status_code == 200
    groups = response.json()
    assert isinstance(groups, list)
    assert len(groups) > 0
    
    # Verify group structure
    group = groups[0]
    assert 'id' in group
    assert 'name' in group
    print("✅ Word's groups retrieved successfully")

@pytest.mark.usefixtures("flask_server", "word_id", "group_id", "study_activity_id")
def test_study_sessions(word_id, group_id, study_activity_id):
    print("\nTesting Study Sessions API...")

    # Create study session
    session_data = {
        "group_id": group_id,
        "study_activity_id": study_activity_id
    }
    response = requests.post(f"{BASE_URL}/api/study_sessions", json=session_data)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    assert response.status_code == 201
    session = response.json()
    assert 'id' in session
    assert 'group_id' in session
    assert 'study_activity_id' in session
    assert 'created_at' in session
    print("✅ Study session created successfully")

    # Get study sessions
    response = requests.get(f"{BASE_URL}/api/study_sessions")
    print(f"Get study sessions status code: {response.status_code}")
    print(f"Get study sessions content: {response.text}")
    assert response.status_code == 200
    sessions = response.json()
    assert isinstance(sessions, list)
    assert len(sessions) > 0
    print("✅ Study sessions retrieved successfully")

    # Verify session structure
    session = sessions[0]
    assert all(key in session for key in [
        'id', 'group_id', 'group_name',
        'study_activity_id', 'activity_name',
        'created_at'
    ])
    print("✅ Session structure verified")

    # Log a review for the session
    review_data = {
        "word_id": word_id,
        "correct": True
    }
    response = requests.post(f"{BASE_URL}/api/study_sessions/{session['id']}/review", json=review_data)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    assert response.status_code == 201
    review = response.json()
    assert 'id' in review
    assert review['word_id'] == word_id
    assert review['status'] == 'correct'
    print("✅ Review logged successfully")

@pytest.mark.usefixtures("flask_server")
def test_dashboard():
    print("\nTesting Dashboard API...")
    
    # Get dashboard stats
    response = requests.get(f"{BASE_URL}/api/dashboard")
    assert response.status_code == 200
    stats = response.json()
    assert 'total_words' in stats
    assert 'total_groups' in stats
    assert 'total_study_sessions' in stats
    print("✅ Dashboard stats retrieved successfully")

if __name__ == "__main__":
    pytest.main(["-v", "test_api.py"])