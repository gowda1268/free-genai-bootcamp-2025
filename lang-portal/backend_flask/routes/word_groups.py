from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from backend_flask.lib.db import db

# Create the blueprint
word_groups_bp = Blueprint('word_groups', __name__)

# Export the blueprint
__all__ = ['word_groups_bp']

@word_groups_bp.route('/api/word_groups', methods=['POST'])
@cross_origin()
def add_word_to_group():
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({'error': 'Invalid request data'}), 400
        
        word_id = data.get('word_id')
        group_id = data.get('group_id')
        
        if not word_id or not group_id:
            return jsonify({'error': 'word_id and group_id are required'}), 400

        cursor = db.cursor()
        try:
            # Check if word exists
            cursor.execute('SELECT * FROM words WHERE id = ?', (word_id,))
            word = cursor.fetchone()
            if not word:
                return jsonify({'error': 'Word not found'}), 404

            # Check if group exists
            cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
            group = cursor.fetchone()
            if not group:
                return jsonify({'error': 'Group not found'}), 404

            # Check if relationship already exists
            cursor.execute('''
                SELECT * FROM word_groups 
                WHERE word_id = ? AND group_id = ?
            ''', (word_id, group_id))
            existing = cursor.fetchone()
            if existing:
                return jsonify({'error': 'Word is already in this group'}), 400

            # Create the relationship
            cursor.execute('''
                INSERT INTO word_groups (word_id, group_id)
                VALUES (?, ?)
            ''', (word_id, group_id))
            
            # Update group's word count
            cursor.execute('''
                UPDATE groups 
                SET words_count = words_count + 1
                WHERE id = ?
            ''', (group_id,))
            
            db.commit()
            
            return jsonify({
                'word_id': word_id,
                'group_id': group_id
            }), 201
        except Exception as e:
            db.rollback()
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@word_groups_bp.route('/api/words/<int:word_id>/groups', methods=['GET'])
@cross_origin()
def get_word_groups(word_id):
    try:
        cursor = db.cursor()
        try:
            # Check if word exists
            cursor.execute('SELECT * FROM words WHERE id = ?', (word_id,))
            word = cursor.fetchone()
            if not word:
                return jsonify({'error': 'Word not found'}), 404

            cursor.execute('''
                SELECT g.* 
                FROM word_groups wg
                JOIN groups g ON wg.group_id = g.id
                WHERE wg.word_id = ?
            ''', (word_id,))
            groups = cursor.fetchall()
            result = []
            for group in groups:
                group_dict = dict(group)
                result.append({
                    'id': group_dict['id'],
                    'name': group_dict['name']
                })
            return jsonify(result), 200
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@word_groups_bp.route('/api/word_groups/<int:word_id>/<int:group_id>', methods=['DELETE'])
@cross_origin()
def remove_word_from_group(word_id, group_id):
    try:
        cursor = db.cursor()
        try:
            # Check if the word exists in the group
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM word_groups 
                WHERE word_id = ? AND group_id = ?
            ''', (word_id, group_id))
            result = cursor.fetchone()
            
            if not result or result['count'] == 0:
                return jsonify({'error': 'Word is not in this group'}), 404
            
            # Delete the word from group
            cursor.execute('''
                DELETE FROM word_groups 
                WHERE word_id = ? AND group_id = ?
            ''', (word_id, group_id))
            
            # Update group's word count
            cursor.execute('''
                UPDATE groups 
                SET words_count = words_count - 1
                WHERE id = ?
            ''', (group_id,))
            
            db.commit()
            
            return jsonify({
                'word_id': word_id,
                'group_id': group_id
            }), 200
        finally:
            cursor.close()
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500