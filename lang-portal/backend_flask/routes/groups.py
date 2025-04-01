from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from backend_flask.lib.db import db

# Export the blueprint
groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/api/groups', methods=['GET'])
@cross_origin()
def get_groups():
    try:
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM groups')
            groups = cursor.fetchall()
            return jsonify([dict(group) for group in groups]), 200
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/api/groups', methods=['POST'])
@cross_origin()
def create_group():
    try:
        data = request.get_json()
        group_name = data.get('group_name')
        
        if not group_name:
            return jsonify({'error': 'group_name is required'}), 400
        
        if not isinstance(group_name, str):
            return jsonify({'error': 'group_name must be a string'}), 400

        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO groups (name) VALUES (?)', (group_name,))
            db.commit()
            
            cursor.execute('SELECT * FROM groups WHERE id = last_insert_rowid()')
            group = cursor.fetchone()
            if group:
                group_dict = dict(group)
                return jsonify({
                    'id': group_dict['id'],
                    'name': group_dict['name']
                }), 201
            else:
                return jsonify({'error': 'Group creation failed'}), 500
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/api/groups/<int:group_id>', methods=['GET'])
@cross_origin()
def get_group(group_id):
    try:
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
            group = cursor.fetchone()
            if group:
                group_dict = dict(group)
                return jsonify({
                    'id': group_dict['id'],
                    'name': group_dict['name']
                }), 200
            else:
                return jsonify({'error': 'Group not found'}), 404
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/api/groups/<int:group_id>', methods=['PUT'])
@cross_origin()
def update_group(group_id):
    try:
        data = request.get_json()
        group_name = data.get('group_name')
        
        if not group_name:
            return jsonify({'error': 'group_name is required'}), 400
        
        if not isinstance(group_name, str):
            return jsonify({'error': 'group_name must be a string'}), 400

        cursor = db.cursor()
        try:
            cursor.execute('UPDATE groups SET name = ? WHERE id = ?', (group_name, group_id))
            db.commit()
            
            cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
            group = cursor.fetchone()
            if group:
                group_dict = dict(group)
                return jsonify({
                    'id': group_dict['id'],
                    'name': group_dict['name']
                }), 200
            else:
                return jsonify({'error': 'Group not found'}), 404
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/api/groups/<int:group_id>', methods=['DELETE'])
@cross_origin()
def delete_group(group_id):
    try:
        cursor = db.cursor()
        try:
            # First check if the group exists
            cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
            group = cursor.fetchone()
            if not group:
                return jsonify({'error': 'Group not found'}), 404
            
            # Delete the group
            cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
            db.commit()
            
            return jsonify({'message': 'Group deleted successfully'}), 200
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/api/groups/<int:group_id>/words', methods=['GET'])
@cross_origin()
def get_group_words(group_id):
    try:
        page = int(request.args.get('page', 1))
        per_page = 20
        offset = (page - 1) * per_page
        
        sort_by = request.args.get('sort_by', 'name')
        order = request.args.get('order', 'asc')
        
        allowed_sort_fields = ['name', 'words_count']
        if sort_by not in allowed_sort_fields:
            return jsonify({'error': f'Invalid sort_by field. Must be one of: {allowed_sort_fields}'}), 400
            
        if order not in ['asc', 'desc']:
            return jsonify({'error': 'order must be either asc or desc'}), 400

        cursor = db.cursor()
        try:
            # Verify group exists
            cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
            group = cursor.fetchone()
            if not group:
                return jsonify({'error': 'Group not found'}), 404

            # Get total count of words in group
            cursor.execute('''
                SELECT COUNT(*) as total 
                FROM word_groups 
                WHERE group_id = ?
            ''', (group_id,))
            total = cursor.fetchone()['total']
            
            # Get words from group with pagination and sorting
            cursor.execute(f'''
                SELECT w.*, 
                       (SELECT COUNT(*) FROM word_review_items WHERE word_id = w.id AND correct = 1) as correct_count,
                       (SELECT COUNT(*) FROM word_review_items WHERE word_id = w.id AND correct = 0) as wrong_count
                FROM words w
                JOIN word_groups wg ON w.id = wg.word_id
                WHERE wg.group_id = ?
                ORDER BY {sort_by} {order}
                LIMIT ? OFFSET ?
            ''', (group_id, per_page, offset))
            
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
__all__ = ['groups_bp']
