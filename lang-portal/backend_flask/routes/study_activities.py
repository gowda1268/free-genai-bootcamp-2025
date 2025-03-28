from flask import jsonify, request
from flask_cors import cross_origin

def register_routes(app):
    @app.route('/api/study-activities', methods=['GET'])
    @cross_origin()
    def get_study_activities():
        cursor = app.db.cursor()
        cursor.execute('SELECT id, name, url, preview_url FROM study_activities')
        activities = cursor.fetchall()
        
        return jsonify([{
            'id': activity['id'],
            'title': activity['name'],
            'launch_url': activity['url'],
            'preview_url': activity['preview_url']
        } for activity in activities])

    @app.route('/api/study-activities/<int:id>', methods=['GET'])
    @cross_origin()
    def get_study_activity(id):
        cursor = app.db.cursor()
        cursor.execute('SELECT id, name, url, preview_url FROM study_activities WHERE id = ?', (id,))
        activity = cursor.fetchone()
        
        if not activity:
            return jsonify({'error': 'Activity not found'}), 404
            
        return jsonify({
            'id': activity['id'],
            'title': activity['name'],
            'launch_url': activity['url'],
            'preview_url': activity['preview_url']
        })