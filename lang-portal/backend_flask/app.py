from flask import Flask, g, jsonify
from flask_cors import CORS
from backend_flask.lib.db import db

from backend_flask.routes.words import words_bp
from backend_flask.routes.groups import groups_bp
from backend_flask.routes.study_sessions import study_sessions_bp
from backend_flask.routes.dashboard import dashboard_bp
from backend_flask.routes.study_activities import study_activities_bp
from backend_flask.routes.word_groups import word_groups_bp

def create_app(test_config=None):
    app = Flask(__name__)
    
    if test_config is None:
        app.config.from_mapping(
            DATABASE='words.db'
        )
    else:
        app.config.update(test_config)
    
    print(f"Using database: {app.config['DATABASE']}")
    try:
        # Initialize the database
        db.init_app(app)
        print("Database connection established successfully")
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise
    
    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    @app.teardown_appcontext
    def close_db(exception):
        db.close(exception)

    # load routes -----------
    app.register_blueprint(words_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(study_sessions_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(study_activities_bp)
    app.register_blueprint(word_groups_bp)

    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error"}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)