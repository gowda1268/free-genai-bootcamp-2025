from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from backend_flask.lib.db import db

# Create the blueprint
words_bp = Blueprint('words', __name__)

# Export the blueprint
__all__ = ['words_bp']

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
                return jsonify({
                    'word': {
                        'id': word_dict['id'],
                        'kanji': word_dict['kanji'],
                        'romaji': word_dict['romaji'],
                        'english': word_dict['english'],
                        'parts': word_dict['parts']
                    }
                }), 201
            else:
                return jsonify({'error': 'Word creation failed'}), 500
        finally:
            cursor.close()
    except Exception as e:
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
        if not data or not isinstance(data, dict):
            return jsonify({'error': 'Invalid request data'}), 400

        # Get current word data
        cursor = db.cursor()
        cursor.execute('SELECT * FROM words WHERE id = ?', (word_id,))
        current_word = cursor.fetchone()
        
        if not current_word:
            return jsonify({'error': 'Word not found'}), 404

        # Prepare update query and parameters
        updates = []
        params = []
        
        if 'kanji' in data:
            updates.append('kanji = ?')
            params.append(data['kanji'])
        if 'romaji' in data:
            updates.append('romaji = ?')
            params.append(data['romaji'])
        if 'english' in data:
            updates.append('english = ?')
            params.append(data['english'])
        if 'parts' in data:
            updates.append('parts = ?')
            params.append(data['parts'])
        
        if not updates:
            return jsonify({'error': 'No fields to update'}), 400

        # Add word_id to parameters
        params.append(word_id)

        try:
            # Build and execute update query
            update_query = f"UPDATE words SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(update_query, params)
            db.commit()
            
            # Get updated word
            cursor.execute('SELECT * FROM words WHERE id = ?', (word_id,))
            updated_word = cursor.fetchone()
            
            return jsonify({
                'message': 'Word updated successfully',
                'word': dict(updated_word)
            })
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
        
        allowed_sort_fields = ['kanji', 'romaji', 'english']
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
                       (SELECT COUNT(*) FROM word_review_items WHERE word_id = w.id AND status = 'correct') as correct_count,
                       (SELECT COUNT(*) FROM word_review_items WHERE word_id = w.id AND status = 'incorrect') as wrong_count
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
