from flask import request, jsonify
from flask_cors import cross_origin
from lib.db import db  # Changed from relative to absolute import
def register_routes(app):
    @app.route('/api/groups', methods=['GET'])
    @cross_origin()
    def get_groups():
        # Logic to retrieve groups
        try:
            cursor = db.cursor()
            cursor.execute('SELECT * FROM groups')
            groups = cursor.fetchall()
            return jsonify(groups), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/groups', methods=['POST'])
    @cross_origin()
    def create_group():
        # Logic to create a new group
        data = request.get_json()
        group_name = data.get('group_name')
        # Add your logic to insert the group into the database
        return jsonify({"message": "Group created successfully"}), 201