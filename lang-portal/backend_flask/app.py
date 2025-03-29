from flask import Flask, jsonify, g
from flask_cors import CORS
from lib.db import Db

import routes.words
import routes.groups
import routes.study_sessions
import routes.dashboard
import routes.study_activities
import routes.word_groups

def get_allowed_origins(app):
    try:
        print("Getting allowed origins...")
        with app.app_context():
            cursor = app.db.cursor()
            cursor.execute('SELECT url FROM study_activities')
            urls = cursor.fetchall()
            origins = set()
            for url in urls:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url['url'])
                    origin = f"{parsed.scheme}://{parsed.netloc}"
                    origins.add(origin)
                except Exception as e:
                    print(f"Error parsing URL: {e}")
                    continue
            print(f"Allowed origins: {origins}")
            return list(origins) if origins else ["*"]
    except Exception as e:
        print(f"Error getting origins: {e}, returning default")
        return ["*"]

def create_app(test_config=None):
    print("Creating app...")
    app = Flask(__name__)
    
    if test_config is None:
        app.config.from_mapping(
            DATABASE='words.db'
        )
    else:
        app.config.update(test_config)
    
    print(f"Using database: {app.config['DATABASE']}")
    try:
        # Initialize the database connection
        app.db = Db(app, app.config['DATABASE'])
        print("Database connection established successfully")
        
        # Setup database tables
        app.db.setup_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise
    
    # Configure CORS
    allowed_origins = get_allowed_origins(app)
    if app.debug:
        allowed_origins.extend(["http://localhost:8080", "http://127.0.0.1:8080"])
    
    CORS(app, resources={
        r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    print(f"CORS configured with origins: {allowed_origins}")

    # Register blueprints
    app.register_blueprint(routes.words.words_bp)
    app.register_blueprint(routes.groups.groups_bp)
    app.register_blueprint(routes.study_sessions.study_sessions_bp)
    app.register_blueprint(routes.dashboard.dashboard_bp)
    app.register_blueprint(routes.study_activities.study_activities_bp)
    
    # Register word_groups routes
    routes.word_groups.register_routes(app)
    
    @app.teardown_appcontext
    def close_db(exception):
        print("Closing database connection...")
        app.db.close()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)