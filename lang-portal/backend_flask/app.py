<<<<<<< HEAD
from flask import Flask, jsonify, g
from flask_cors import CORS
=======
from flask import Flask, g
from flask_cors import CORS

>>>>>>> 704c651a134e70ae6424883b8faed7b515bdd8b0
from lib.db import Db

import routes.words
import routes.groups
import routes.study_sessions
import routes.dashboard
import routes.study_activities
<<<<<<< HEAD
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
=======

def get_allowed_origins(app):
    try:
        cursor = app.db.cursor()
        cursor.execute('SELECT url FROM study_activities')
        urls = cursor.fetchall()
        # Convert URLs to origins (e.g., https://example.com/app -> https://example.com)
        origins = set()
        for url in urls:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url['url'])
                origin = f"{parsed.scheme}://{parsed.netloc}"
                origins.add(origin)
            except:
                continue
        return list(origins) if origins else ["*"]
    except:
        return ["*"]  # Fallback to allow all origins if there's an error

def create_app(test_config=None):
>>>>>>> 704c651a134e70ae6424883b8faed7b515bdd8b0
    app = Flask(__name__)
    
    if test_config is None:
        app.config.from_mapping(
            DATABASE='words.db'
        )
    else:
        app.config.update(test_config)
    
<<<<<<< HEAD
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
    
=======
    # Initialize database first since we need it for CORS configuration
    app.db = Db(database=app.config['DATABASE'])
    
    # Get allowed origins from study_activities table
    allowed_origins = get_allowed_origins(app)
    
    # In development, add localhost to allowed origins
    if app.debug:
        allowed_origins.extend(["http://localhost:8080", "http://127.0.0.1:8080"])
    
    # Configure CORS with combined origins
>>>>>>> 704c651a134e70ae6424883b8faed7b515bdd8b0
    CORS(app, resources={
        r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
<<<<<<< HEAD
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
=======

    # Close database connection
    @app.teardown_appcontext
    def close_db(exception):
        app.db.close()

    # load routes -----------
    routes.words.load(app)
    routes.groups.load(app)
    routes.study_sessions.load(app)
    routes.dashboard.load(app)
    routes.study_activities.load(app)
    
    return app

app = create_app()

if __name__ == '__main__':
>>>>>>> 704c651a134e70ae6424883b8faed7b515bdd8b0
    app.run(debug=True)