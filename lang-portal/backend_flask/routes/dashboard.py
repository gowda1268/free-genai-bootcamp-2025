from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from backend_flask.lib.db import db

# Export the blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard', methods=['GET'])
@cross_origin()
def get_dashboard():
    try:
        cursor = db.cursor()
        try:
            # Get total words
            cursor.execute('SELECT COUNT(*) as total_words FROM words')
            total_words = cursor.fetchone()['total_words']
            
            # Get total groups
            cursor.execute('SELECT COUNT(*) as total_groups FROM groups')
            total_groups = cursor.fetchone()['total_groups']
            
            # Get total study sessions
            cursor.execute('SELECT COUNT(*) as total_sessions FROM study_sessions')
            total_sessions = cursor.fetchone()['total_sessions']
            
            # Get total correct and wrong reviews
            cursor.execute('''
                SELECT 
                    COUNT(CASE WHEN status = 'correct' THEN 1 END) as correct_reviews,
                    COUNT(CASE WHEN status = 'incorrect' THEN 1 END) as wrong_reviews
                FROM word_review_items
            ''')
            review_stats = cursor.fetchone()
            
            return jsonify({
                'total_words': total_words,
                'total_groups': total_groups,
                'total_study_sessions': total_sessions,
                'correct_reviews': review_stats['correct_reviews'] or 0,
                'wrong_reviews': review_stats['wrong_reviews'] or 0
            }), 200
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/recent-session', methods=['GET'])
@cross_origin()
def get_recent_session():
    try:
        cursor = db.cursor()
        try:
            # Get the most recent study session with activity name and results
            cursor.execute('''
                SELECT 
                    ss.id,
                    ss.group_id,
                    sa.name as activity_name,
                    ss.created_at,
                    COUNT(CASE WHEN wri.correct = 1 THEN 1 END) as correct_count,
                    COUNT(CASE WHEN wri.correct = 0 THEN 1 END) as wrong_count
                FROM study_sessions ss
                JOIN study_activities sa ON ss.study_activity_id = sa.id
                LEFT JOIN word_review_items wri ON ss.id = wri.study_session_id
                GROUP BY ss.id
                ORDER BY ss.created_at DESC
                LIMIT 1
            ''')
            
            session = cursor.fetchone()
            
            if not session:
                return jsonify(None)
            
            return jsonify(dict(session))
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@cross_origin()
def get_stats():
    try:
        cursor = db.cursor()
        try:
            # Get total words
            cursor.execute('SELECT COUNT(*) as total_words FROM words')
            total_words = cursor.fetchone()['total_words']
            
            # Get total correct and wrong reviews
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as total_correct,
                    SUM(CASE WHEN correct = 0 THEN 1 ELSE 0 END) as total_wrong
                FROM word_review_items
            ''')
            reviews = cursor.fetchone()
            
            return jsonify({
                'total_words': total_words,
                'total_correct': reviews['total_correct'] or 0,
                'total_wrong': reviews['total_wrong'] or 0
            })
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Export the blueprint
__all__ = ['dashboard_bp']
