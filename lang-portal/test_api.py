import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_words():
    print("\nTesting Words API...")
    
    # Create a new word
    word_data = {
        "word": "新しい",
        "parts": "形容詞"
    }
    response = requests.post(f"{BASE_URL}/words", json=word_data)
    assert response.status_code == 201
    word_id = response.json()['word']['id']
    print("✅ Word created successfully")
    
    # Get all words
    response = requests.get(f"{BASE_URL}/words")
    assert response.status_code == 200
    words = response.json()
    assert len(words) > 0
    print("✅ Words retrieved successfully")
    
    return word_id

def test_groups():
    print("\nTesting Groups API...")
    
    # Create a new group
    group_data = {
        "name": "Adjectives"
    }
    response = requests.post(f"{BASE_URL}/groups", json=group_data)
    assert response.status_code == 201
    group_id = response.json()['group']['id']
    print("✅ Group created successfully")
    
    # Get all groups
    response = requests.get(f"{BASE_URL}/groups")
    assert response.status_code == 200
    groups = response.json()
    assert len(groups) > 0
    print("✅ Groups retrieved successfully")
    
    return group_id

def test_word_groups(word_id, group_id):
    print("\nTesting Word-Group Relationship...")
    
    # Add word to group
    response = requests.post(f"{BASE_URL}/word-groups", json={
        "word_id": word_id,
        "group_id": group_id
    })
    assert response.status_code == 201
    print("✅ Word added to group successfully")
    
    # Get group words
    response = requests.get(f"{BASE_URL}/groups/{group_id}")
    assert response.status_code == 200
    words = response.json()
    assert len(words) > 0
    print("✅ Group words retrieved successfully")

def test_study_sessions(word_id, group_id):
    print("\nTesting Study Sessions...")
    
    # Create study session
    response = requests.post(f"{BASE_URL}/study-sessions", json={
        "group_id": group_id,
        "study_activity_id": 1  # Assuming we have a study activity with ID 1
    })
    assert response.status_code == 201
    session_id = response.json()['session_id']
    print("✅ Study session created successfully")
    
    # Log review
    response = requests.post(f"{BASE_URL}/study-sessions/{session_id}/review", json={
        "word_id": word_id,
        "correct": True
    })
    assert response.status_code == 201
    print("✅ Review logged successfully")
    
    # Get session details
    response = requests.get(f"{BASE_URL}/study-sessions/{session_id}")
    assert response.status_code == 200
    session = response.json()
    assert len(session['reviews']) > 0
    print("✅ Session details retrieved successfully")

def test_dashboard():
    print("\nTesting Dashboard...")
    
    # Get dashboard stats
    response = requests.get(f"{BASE_URL}/dashboard/stats")
    assert response.status_code == 200
    stats = response.json()
    assert 'total_words' in stats
    print("✅ Dashboard stats retrieved successfully")
    
    # Get word statistics
    response = requests.get(f"{BASE_URL}/dashboard/word-stats")
    assert response.status_code == 200
    word_stats = response.json()
    assert len(word_stats) > 0
    print("✅ Word statistics retrieved successfully")
    
    # Get group statistics
    response = requests.get(f"{BASE_URL}/dashboard/group-stats")
    assert response.status_code == 200
    group_stats = response.json()
    assert len(group_stats) > 0
    print("✅ Group statistics retrieved successfully")

def main():
    print("Starting API Tests...")
    
    # Make sure the server is running
    try:
        response = requests.get("http://127.0.0.1:5000")
        assert response.status_code == 200
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please start the Flask application first.")
        return
    
    # Run tests
    word_id = test_words()
    group_id = test_groups()
    test_word_groups(word_id, group_id)
    test_study_sessions(word_id, group_id)
    test_dashboard()
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main()