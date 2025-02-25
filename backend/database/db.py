# backend/database/db.py
import sqlite3
import os
from flask import g

DATABASE = 'jobs.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def initialize_db():
    # Create the database if it doesn't exist
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            url TEXT NOT NULL,
            source TEXT NOT NULL,
            date_posted TEXT
        )
        ''')
        
        conn.commit()
        conn.close()