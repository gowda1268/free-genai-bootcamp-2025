from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from backend_flask.lib.db import db

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

@study_activities_bp.route('/api/study-activities', methods=['POST'])
@cross_origin()
def create_study_activity():
    try:
        data = request.get_json()
        
        name = data.get('name')
        url = data.get('url')
        preview_url = data.get('preview_url')
        
        if not name or not url:
            return jsonify({'error': 'name and url are required'}), 400

        cursor = db.cursor()
        try:
            cursor.execute('''
                INSERT INTO study_activities (name, url, preview_url)
                VALUES (?, ?, ?)
            ''', (name, url, preview_url))
            db.commit()
            
            cursor.execute('SELECT * FROM study_activities WHERE id = last_insert_rowid()')
            activity = cursor.fetchone()
            if activity:
                activity_dict = dict(activity)
                return jsonify({
                    'id': activity_dict['id'],
                    'name': activity_dict['name'],
                    'url': activity_dict['url'],
                    'preview_url': activity_dict['preview_url']
                }), 201
            else:
                return jsonify({'error': 'Activity creation failed'}), 500
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
