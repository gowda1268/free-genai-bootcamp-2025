import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

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
    words = response.json()
    assert isinstance(words, list)
    assert len(words) > 0
    print(f"Found {len(words)} words")
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
    
    return word_id

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
    
    return group_id

def test_word_groups(word_id, group_id):
    print("\nTesting Word-Group Relationship...")
    
    # Verify word exists
    response = requests.get(f"{BASE_URL}/api/words/{word_id}")
    assert response.status_code == 200, f"Word with id {word_id} not found"
    
    # Verify group exists
    response = requests.get(f"{BASE_URL}/api/groups/{group_id}")
    assert response.status_code == 200, f"Group with id {group_id} not found"
    
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

def test_study_sessions(word_id, group_id):
    print("\nTesting Study Sessions API...")
    
    # Create study session
    session_data = {
        "word_id": word_id,
        "group_id": group_id,
        "duration": 30,
        "correct_answers": 5,
        "total_questions": 10
    }
    response = requests.post(f"{BASE_URL}/api/study_sessions", json=session_data)
    assert response.status_code == 201
    session = response.json()
    assert 'id' in session
    assert 'word_id' in session
    assert 'group_id' in session
    assert 'duration' in session
    assert 'correct_answers' in session
    assert 'total_questions' in session
    assert 'created_at' in session
    print("✅ Study session created successfully")
    
    # Get study sessions
    response = requests.get(f"{BASE_URL}/api/study_sessions")
    assert response.status_code == 200
    sessions = response.json()
    assert isinstance(sessions, list)
    assert len(sessions) > 0
    
    # Verify session structure
    session = sessions[0]
    assert all(key in session for key in [
        'id', 'word_id', 'word_kanji', 'group_id', 'group_name',
        'duration', 'correct_answers', 'total_questions', 'created_at'
    ])
    print("✅ Study sessions retrieved successfully")

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

def main():
    print("Starting API tests...")
    
    try:
        # Test words
        word_id = test_words()
        
        # Test groups
        group_id = test_groups()
        
        # Test word-groups relationship
        test_word_groups(word_id, group_id)
        
        # Test study sessions
        test_study_sessions(word_id, group_id)
        
        # Test dashboard
        test_dashboard()
        
        print("\n✅ All tests passed successfully!")
    except AssertionError as e:
        print(f"❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()