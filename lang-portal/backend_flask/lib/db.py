import sqlite3
from flask import g

class Db:
    def __init__(self, app=None, database='words.db'):
        self.database = database
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.teardown_appcontext(self.close)

    def get_db(self):
        if 'db' not in g:
            g.db = sqlite3.connect(
                self.database,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        return g.db

    def close(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def execute(self, statement, args=()):
        db = self.get_db()
        return db.execute(statement, args)

    def commit(self):
        db = self.get_db()
        db.commit()

    def cursor(self):
        return self.get_db().cursor()

    def setup_tables(self):
        with self.app.app_context():
            cursor = self.cursor()
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kanji TEXT NOT NULL,
                    romaji TEXT NOT NULL,
                    english TEXT NOT NULL,
                    parts TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    words_count INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS word_groups (
                    word_id INTEGER NOT NULL,
                    group_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (word_id, group_id),
                    FOREIGN KEY (word_id) REFERENCES words(id),
                    FOREIGN KEY (group_id) REFERENCES groups(id)
                );

                CREATE TABLE IF NOT EXISTS study_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    preview_url TEXT
                );

                CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    study_activity_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups(id),
                    FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
                );

                CREATE TABLE IF NOT EXISTS word_review_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word_id INTEGER NOT NULL,
                    study_session_id INTEGER NOT NULL,
                    correct BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (word_id) REFERENCES words(id),
                    FOREIGN KEY (study_session_id) REFERENCES study_sessions(id)
                );
            ''')
            self.commit()

# Create an instance of the Db class
db = Db()