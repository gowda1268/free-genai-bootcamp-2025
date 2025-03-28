from flask import Flask, jsonify, g
from flask_cors import CORS
from lib.db import Db

import routes.words
import routes.groups
import routes.study_sessions
import routes.dashboard
import routes.study_activities

def get_allowed_origins(app):
    try:
        print("Getting allowed origins...")
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
            except:
                continue
        print(f"Allowed origins: {origins}")
        return list(origins) if origins else ["*"]
    except:
        print("Error getting origins, returning default")
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
        app.db = Db(database=app.config['DATABASE'])
        app.db.row_factory = lambda cursor, row: dict((col[0], row[idx]) for idx, col in enumerate(cursor.description))
        print("Database connection established successfully")
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise
    
    print("Initializing database tables...")
    with app.app_context():
        try:
            cursor = app.db.cursor()
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kanji TEXT NOT NULL,
                    romaji TEXT NOT NULL,
                    english TEXT NOT NULL,
                    parts TEXT NOT NULL,
                    correct_count INTEGER DEFAULT 0,
                    wrong_count INTEGER DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    words_count INTEGER DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS word_groups (
                    word_id INTEGER,
                    group_id INTEGER,
                    FOREIGN KEY (word_id) REFERENCES words(id),
                    FOREIGN KEY (group_id) REFERENCES groups(id),
                    PRIMARY KEY (word_id, group_id)
                );
                
                CREATE TABLE IF NOT EXISTS study_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    preview_url TEXT
                );
                
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    study_activity_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups(id),
                    FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
                );
                
                CREATE TABLE IF NOT EXISTS word_review_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    study_session_id INTEGER,
                    word_id INTEGER,
                    correct INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (study_session_id) REFERENCES study_sessions(id),
                    FOREIGN KEY (word_id) REFERENCES words(id)
                );
                
                CREATE TABLE IF NOT EXISTS word_reviews (
                    word_id INTEGER,
                    correct_count INTEGER DEFAULT 0,
                    wrong_count INTEGER DEFAULT 0,
                    FOREIGN KEY (word_id) REFERENCES words(id),
                    PRIMARY KEY (word_id)
                );
                
                -- Create indexes for better performance
                CREATE INDEX IF NOT EXISTS idx_word_reviews_word_id ON word_reviews(word_id);
                CREATE INDEX IF NOT EXISTS idx_word_review_items_word_id ON word_review_items(word_id);
                CREATE INDEX IF NOT EXISTS idx_word_review_items_study_session_id ON word_review_items(study_session_id);
                CREATE INDEX IF NOT EXISTS idx_study_sessions_group_id ON study_sessions(group_id);
                CREATE INDEX IF NOT EXISTS idx_study_sessions_study_activity_id ON study_sessions(study_activity_id);
            ''')
            app.db.commit()
            print("Database tables initialized successfully")
            
            # Add some sample data
            cursor.execute('''
                INSERT INTO words (kanji, romaji, english, parts)
                VALUES 
                ('新しい', 'atarashii', 'new', '形容詞'),
                ('美しい', 'utsukushii', 'beautiful', '形容詞'),
                ('速い', 'hayai', 'fast', '形容詞')
            ''')
            app.db.commit()
            print("Sample data added")
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
            raise
    
    print("Configuring CORS...")
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

    @app.teardown_appcontext
    def close_db(exception):
        print("Closing database connection...")
        app.db.close()

    # Define root route
    @app.route('/')
    def index():
        return jsonify({"message": "Welcome to the Language Learning API!"}), 200

    # Register routes using the imported functions
    routes.words.register_routes(app)
    routes.groups.register_routes(app)
    routes.study_sessions.register_routes(app)
    routes.dashboard.register_routes(app)
    routes.study_activities.register_routes(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)