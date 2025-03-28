from flask import request, jsonify
from flask_cors import cross_origin
from lib.db import db  # Changed from relative to absolute import  

def register_routes(app):
    @app.route('/api/study_sessions', methods=['POST'])
    @cross_origin()
    def create_study_session():
        # Get JSON data from the request
        data = request.get_json()
        
        # Extract group_id and study_activity_id from the data
        group_id = data.get('group_id')
        study_activity_id = data.get('study_activity_id')

        # Validate input
        if not group_id or not study_activity_id:
            return jsonify({"error": "group_id and study_activity_id are required."}), 400

        # Call your database function to create the study session
        try:
            new_session_id = db.create_study_session_in_db(group_id, study_activity_id)
            return jsonify({"message": "Study session created successfully", "session_id": new_session_id}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/study_sessions/<int:id>/review', methods=['POST'])
    @cross_origin()
    def log_review(id):
        # Get JSON data from the request
        data = request.get_json()
        
        # Extract word_id and correct status from the data
        word_id = data.get('word_id')
        correct = data.get('correct')

        # Validate input
        if word_id is None or correct is None:
            return jsonify({"error": "word_id and correct status are required."}), 400

        # Call your database function to log the review
        try:
            db.log_review_in_db(id, word_id, correct)  # Use the db instance to call the method
            return jsonify({"message": "Review logged successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/study-sessions/reset', methods=['POST'])
    @cross_origin()
    def reset_study_sessions():
        try:
            cursor = db.cursor()  # Use the db instance to get the cursor
            
            # First delete all word review items since they have foreign key constraints
            cursor.execute('DELETE FROM word_review_items')
            
            # Then delete all study sessions
            cursor.execute('DELETE FROM study_sessions')
            
            db.commit()  # Use the db instance to commit changes
            
            return jsonify({"message": "Study history cleared successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500