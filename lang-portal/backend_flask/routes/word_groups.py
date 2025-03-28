from flask import request, jsonify
from flask_cors import cross_origin
from lib.db import Db

def register_routes(app):
    @app.route('/api/word-groups', methods=['POST'])
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

            cursor = app.db.cursor()
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
            
            app.db.commit()
            
            return jsonify({'message': 'Word added to group successfully'}), 201
        except Exception as e:
            print(f"Error adding word to group: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/word-groups/<int:word_id>/<int:group_id>', methods=['DELETE'])
    @cross_origin()
    def remove_word_from_group(word_id, group_id):
        try:
            cursor = app.db.cursor()
            
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
            
            app.db.commit()
            
            return jsonify({'message': 'Word removed from group successfully'}), 200
        except Exception as e:
            print(f"Error removing word from group: {str(e)}")
            return jsonify({'error': str(e)}), 500