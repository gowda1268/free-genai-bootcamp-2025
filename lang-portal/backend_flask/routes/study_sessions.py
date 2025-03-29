from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from lib.db import db

# Export the blueprint
study_sessions_bp = Blueprint('study_sessions', __name__)

@study_sessions_bp.route('/api/study_sessions', methods=['GET'])
@cross_origin()
def list_study_sessions():
    try:
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT s.*, g.name as group_name, sa.name as activity_name
                FROM study_sessions s
                JOIN groups g ON s.group_id = g.id
                JOIN study_activities sa ON s.study_activity_id = sa.id
                ORDER BY s.created_at DESC
            ''')
            sessions = cursor.fetchall()
            result = []
            for session in sessions:
                session_dict = dict(session)
                result.append({
                    'id': session_dict['id'],
                    'group_id': session_dict['group_id'],
                    'group_name': session_dict['group_name'],
                    'study_activity_id': session_dict['study_activity_id'],
                    'activity_name': session_dict['activity_name'],
                    'created_at': session_dict['created_at']
                })
            return jsonify(result), 200
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_sessions_bp.route('/api/study_sessions', methods=['POST'])
@cross_origin()
def create_study_session():
    try:
        data = request.get_json()
        
        group_id = data.get('group_id')
        study_activity_id = data.get('study_activity_id')
        
        if not group_id or not study_activity_id:
            return jsonify({'error': 'group_id and study_activity_id are required'}), 400

        cursor = db.cursor()
        try:
            # Verify group exists
            cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
            group = cursor.fetchone()
            if not group:
                return jsonify({'error': 'Group not found'}), 404

            # Verify study activity exists
            cursor.execute('SELECT * FROM study_activities WHERE id = ?', (study_activity_id,))
            activity = cursor.fetchone()
            if not activity:
                return jsonify({'error': 'Study activity not found'}), 404

            # Create study session
            cursor.execute('''
                INSERT INTO study_sessions (group_id, study_activity_id)
                VALUES (?, ?)
            ''', (group_id, study_activity_id))
            db.commit()
            
            # Get the created session
            cursor.execute('SELECT * FROM study_sessions WHERE id = last_insert_rowid()')
            session = cursor.fetchone()
            if session:
                session_dict = dict(session)
                return jsonify({
                    'id': session_dict['id'],
                    'group_id': session_dict['group_id'],
                    'study_activity_id': session_dict['study_activity_id'],
                    'created_at': session_dict['created_at']
                }), 201
            else:
                return jsonify({'error': 'Study session creation failed'}), 500
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_sessions_bp.route('/api/study_sessions/<int:session_id>/review', methods=['POST'])
@cross_origin()
def log_review(session_id):
    try:
        data = request.get_json()
        
        word_id = data.get('word_id')
        correct = data.get('correct')
        
        if not word_id or correct is None:
            return jsonify({'error': 'word_id and correct are required'}), 400

        if not isinstance(correct, bool):
            return jsonify({'error': 'correct must be a boolean value'}), 400

        cursor = db.cursor()
        try:
            # Verify study session exists
            cursor.execute('SELECT * FROM study_sessions WHERE id = ?', (session_id,))
            session = cursor.fetchone()
            if not session:
                return jsonify({'error': 'Study session not found'}), 404

            # Verify word exists
            cursor.execute('SELECT * FROM words WHERE id = ?', (word_id,))
            word = cursor.fetchone()
            if not word:
                return jsonify({'error': 'Word not found'}), 404

            # Create review item
            cursor.execute('''
                INSERT INTO word_review_items (word_id, study_session_id, correct)
                VALUES (?, ?, ?)
            ''', (word_id, session_id, correct))
            db.commit()
            
            # Get the created review item
            cursor.execute('SELECT * FROM word_review_items WHERE id = last_insert_rowid()')
            review = cursor.fetchone()
            if review:
                review_dict = dict(review)
                return jsonify({
                    'id': review_dict['id'],
                    'word_id': review_dict['word_id'],
                    'study_session_id': review_dict['study_session_id'],
                    'correct': review_dict['correct'],
                    'created_at': review_dict['created_at']
                }), 201
            else:
                return jsonify({'error': 'Review creation failed'}), 500
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_sessions_bp.route('/api/study-sessions/reset', methods=['POST'])
@cross_origin()
def reset_study_sessions():
    try:
        cursor = db.cursor()
        try:
            cursor.execute('DELETE FROM word_review_items')
            cursor.execute('DELETE FROM study_sessions')
            db.commit()
            return jsonify({"message": "Study sessions reset successfully"}), 200
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Export the blueprint
__all__ = ['study_sessions_bp']