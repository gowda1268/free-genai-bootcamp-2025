<<<<<<< HEAD
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from lib.db import db

# Export the blueprint
words_bp = Blueprint('words', __name__)

@words_bp.route('/api/words', methods=['POST'])
@cross_origin()
def create_word():
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data or not isinstance(data, dict):
            return jsonify({'error': 'Invalid request data'}), 400
        
        kanji = data.get('kanji')
        romaji = data.get('romaji')
        english = data.get('english')
        parts = data.get('parts', '')  # Default to empty string if not provided
        
        if not all([kanji, romaji, english]):
            return jsonify({'error': 'kanji, romaji, and english are required'}), 400

        cursor = db.cursor()
        try:
            cursor.execute('''
                INSERT INTO words (kanji, romaji, english, parts)
                VALUES (?, ?, ?, ?)
            ''', (kanji, romaji, english, parts))
            db.commit()
            
            # Get the last inserted word
            cursor.execute('''
                SELECT * FROM words WHERE id = last_insert_rowid()
            ''')
            word = cursor.fetchone()
            
            if word:
                word_dict = dict(word)
                print(f"Created word: {word_dict['kanji']}")
                return jsonify({'word': {
                    'id': word_dict['id'],
                    'kanji': word_dict['kanji'],
                    'romaji': word_dict['romaji'],
                    'english': word_dict['english'],
                    'parts': word_dict['parts']
                }}), 201
            else:
                return jsonify({'error': 'Word creation failed'}), 500
        finally:
            cursor.close()
    except Exception as e:
        print(f"Error creating word: {str(e)}")
        return jsonify({'error': str(e)}), 500

@words_bp.route('/api/words/<int:word_id>', methods=['GET'])
@cross_origin()
def get_word(word_id):
    try:
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM words WHERE id = ?', (word_id,))
            word = cursor.fetchone()
            if word:
                word_dict = dict(word)
                return jsonify({
                    'id': word_dict['id'],
                    'kanji': word_dict['kanji'],
                    'romaji': word_dict['romaji'],
                    'english': word_dict['english'],
                    'parts': word_dict['parts']
                }), 200
            else:
                return jsonify({'error': 'Word not found'}), 404
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@words_bp.route('/api/words/<int:word_id>', methods=['PUT'])
@cross_origin()
def update_word(word_id):
    try:
        data = request.get_json()
        cursor = db.cursor()
        try:
            cursor.execute('''
                UPDATE words SET kanji = ?, romaji = ?, english = ?, parts = ?
                WHERE id = ?
            ''', (data['kanji'], data['romaji'], data['english'], data['parts'], word_id))
            db.commit()
            return jsonify({'message': 'Word updated successfully'})
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@words_bp.route('/api/words/<int:word_id>', methods=['DELETE'])
@cross_origin()
def delete_word(word_id):
    try:
        cursor = db.cursor()
        try:
            cursor.execute('DELETE FROM words WHERE id = ?', (word_id,))
            db.commit()
            return jsonify({'message': 'Word deleted successfully'})
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@words_bp.route('/api/words', methods=['GET'])
@cross_origin()
def list_words():
    try:
        page = int(request.args.get('page', 1))
        per_page = 20
        offset = (page - 1) * per_page
        
        sort_by = request.args.get('sort_by', 'kanji')
        order = request.args.get('order', 'asc')
        
        allowed_sort_fields = ['kanji', 'romaji', 'english', 'correct_count', 'wrong_count']
        if sort_by not in allowed_sort_fields:
            return jsonify({'error': f'Invalid sort_by field. Must be one of: {allowed_sort_fields}'}), 400
            
        if order not in ['asc', 'desc']:
            return jsonify({'error': 'order must be either asc or desc'}), 400

        cursor = db.cursor()
        try:
            # Get total count
            cursor.execute('SELECT COUNT(*) as total FROM words')
            total = cursor.fetchone()['total']
            
            # Get words with pagination and sorting
            cursor.execute(f'''
                SELECT w.*, 
                       (SELECT COUNT(*) FROM word_review_items WHERE word_id = w.id AND correct = 1) as correct_count,
                       (SELECT COUNT(*) FROM word_review_items WHERE word_id = w.id AND correct = 0) as wrong_count
                FROM words w
                ORDER BY {sort_by} {order}
                LIMIT ? OFFSET ?
            ''', (per_page, offset))
            
            words = cursor.fetchall()
            
            return jsonify({
                'total': total,
                'page': page,
                'per_page': per_page,
                'words': [dict(word) for word in words]
            }), 200
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Export the blueprint
__all__ = ['words_bp']
=======
from flask import request, jsonify, g
from flask_cors import cross_origin
import json

def load(app):
  # Endpoint: GET /words with pagination (50 words per page)
  @app.route('/words', methods=['GET'])
  @cross_origin()
  def get_words():
    try:
      cursor = app.db.cursor()

      # Get the current page number from query parameters (default is 1)
      page = int(request.args.get('page', 1))
      # Ensure page number is positive
      page = max(1, page)
      words_per_page = 50
      offset = (page - 1) * words_per_page

      # Get sorting parameters from the query string
      sort_by = request.args.get('sort_by', 'kanji')  # Default to sorting by 'kanji'
      order = request.args.get('order', 'asc')  # Default to ascending order

      # Validate sort_by and order
      valid_columns = ['kanji', 'romaji', 'english', 'correct_count', 'wrong_count']
      if sort_by not in valid_columns:
        sort_by = 'kanji'
      if order not in ['asc', 'desc']:
        order = 'asc'

      # Query to fetch words with sorting
      cursor.execute(f'''
        SELECT w.id, w.kanji, w.romaji, w.english, 
            COALESCE(r.correct_count, 0) AS correct_count,
            COALESCE(r.wrong_count, 0) AS wrong_count
        FROM words w
        LEFT JOIN word_reviews r ON w.id = r.word_id
        ORDER BY {sort_by} {order}
        LIMIT ? OFFSET ?
      ''', (words_per_page, offset))

      words = cursor.fetchall()

      # Query the total number of words
      cursor.execute('SELECT COUNT(*) FROM words')
      total_words = cursor.fetchone()[0]
      total_pages = (total_words + words_per_page - 1) // words_per_page

      # Format the response
      words_data = []
      for word in words:
        words_data.append({
          "id": word["id"],
          "kanji": word["kanji"],
          "romaji": word["romaji"],
          "english": word["english"],
          "correct_count": word["correct_count"],
          "wrong_count": word["wrong_count"]
        })

      return jsonify({
        "words": words_data,
        "total_pages": total_pages,
        "current_page": page,
        "total_words": total_words
      })

    except Exception as e:
      return jsonify({"error": str(e)}), 500
    finally:
      app.db.close()

  # Endpoint: GET /words/:id to get a single word with its details
  @app.route('/words/<int:word_id>', methods=['GET'])
  @cross_origin()
  def get_word(word_id):
    try:
      cursor = app.db.cursor()
      
      # Query to fetch the word and its details
      cursor.execute('''
        SELECT w.id, w.kanji, w.romaji, w.english,
               COALESCE(r.correct_count, 0) AS correct_count,
               COALESCE(r.wrong_count, 0) AS wrong_count,
               GROUP_CONCAT(DISTINCT g.id || '::' || g.name) as groups
        FROM words w
        LEFT JOIN word_reviews r ON w.id = r.word_id
        LEFT JOIN word_groups wg ON w.id = wg.word_id
        LEFT JOIN groups g ON wg.group_id = g.id
        WHERE w.id = ?
        GROUP BY w.id
      ''', (word_id,))
      
      word = cursor.fetchone()
      
      if not word:
        return jsonify({"error": "Word not found"}), 404
      
      # Parse the groups string into a list of group objects
      groups = []
      if word["groups"]:
        for group_str in word["groups"].split(','):
          group_id, group_name = group_str.split('::')
          groups.append({
            "id": int(group_id),
            "name": group_name
          })
      
      return jsonify({
        "word": {
          "id": word["id"],
          "kanji": word["kanji"],
          "romaji": word["romaji"],
          "english": word["english"],
          "correct_count": word["correct_count"],
          "wrong_count": word["wrong_count"],
          "groups": groups
        }
      })
      
    except Exception as e:
      return jsonify({"error": str(e)}), 500
>>>>>>> 704c651a134e70ae6424883b8faed7b515bdd8b0
