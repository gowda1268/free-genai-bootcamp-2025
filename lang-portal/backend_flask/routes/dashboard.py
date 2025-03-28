from flask import request, jsonify
from flask_cors import cross_origin
from lib.db import db  # Changed from relative to absolute import
def register_routes(app):
    @app.route('/dashboard/recent-session', methods=['GET'])
    @cross_origin()
    def get_recent_session():
        try:
            cursor = app.db.cursor()
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
            
            return jsonify({
                "id": session["id"],
                "group_id": session["group_id"],
                "activity_name": session["activity_name"],
                "created_at": session["created_at"],
                "correct_count": session["correct_count"],
                "wrong_count": session["wrong_count"]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500