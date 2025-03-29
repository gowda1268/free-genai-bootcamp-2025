from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from lib.db import db

# Export the blueprint
study_activities_bp = Blueprint('study_activities', __name__)

@study_activities_bp.route('/api/study-activities', methods=['GET'])
@cross_origin()
def get_study_activities():
    try:
        cursor = db.cursor()
        try:
            cursor.execute('SELECT id, name, url, preview_url FROM study_activities')
            activities = cursor.fetchall()
            
            return jsonify([{
                'id': activity[0],
                'title': activity[1],
                'launch_url': activity[2],
                'preview_url': activity[3]
            } for activity in activities])
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_activities_bp.route('/api/study-activities/<int:id>', methods=['GET'])
@cross_origin()
def get_study_activity(id):
    try:
        cursor = db.cursor()
        try:
            cursor.execute('SELECT id, name, url, preview_url FROM study_activities WHERE id = ?', (id,))
            activity = cursor.fetchone()
            
            if not activity:
                return jsonify({'error': 'Activity not found'}), 404
                
            return jsonify({
                'id': activity[0],
                'title': activity[1],
                'launch_url': activity[2],
                'preview_url': activity[3]
            })
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Export the blueprint
__all__ = ['study_activities_bp']