from flask import request, jsonify
from flask_cors import cross_origin
from lib.db import Db

def register_routes(app):
    @app.route('/api/words', methods=['GET'])
    @cross_origin()
    def get_words():
        try:
            print("Getting words...")
            cursor = app.db.cursor()
            cursor.execute('SELECT * FROM words')
            words = cursor.fetchall()
            
            print(f"Found {len(words)} words")
            for word in words:
                print(f"Word: {word}")
            
            return jsonify(words), 200
        except Exception as e:
            print(f"Error getting words: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/words', methods=['POST'])
    @cross_origin()
    def create_word():
        try:
            print("Creating word...")
            data = request.get_json()
            print(f"Received data: {data}")
            
            if not data or not isinstance(data, dict):
                return jsonify({'error': 'Invalid request data'}), 400
            
            word = data.get('word')
            parts = data.get('parts', '')  # Default to empty string if not provided
            if not word:
                return jsonify({'error': 'Word is required'}), 400

            cursor = app.db.cursor()
            cursor.execute('INSERT INTO words (kanji, romaji, english, parts) VALUES (?, ?, ?, ?)', 
                          (word, '', '', parts))
            app.db.commit()
            print(f"Created word: {word}")
            
            return jsonify({'message': 'Word created successfully', 'word': word}), 201
        except Exception as e:
            print(f"Error creating word: {str(e)}")
            return jsonify({'error': str(e)}), 500