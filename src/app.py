from flask import Flask, request, jsonify, abort
from mysql.connector import Error

import mysql.connector

app = Flask(__name__)

# Configure your MySQL connection
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_mysql_user',
    'password': 'your_mysql_password',
    'database': 'notes_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Ensure the notes table exists
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            title VARCHAR(255),
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

def get_user_id():
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        abort(400, description="Missing X-User-Id header")
    return user_id

@app.route('/notes', methods=['POST'])
def create_note():
    user_id = get_user_id()
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    if not title or not content:
        abort(400, description="Missing title or content")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (user_id, title, content) VALUES (%s, %s, %s)",
        (user_id, title, content)
    )
    conn.commit()
    note_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({'id': note_id, 'title': title, 'content': content}), 201

@app.route('/notes', methods=['GET'])
def list_notes():
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, title, content, created_at FROM notes WHERE user_id = %s",
        (user_id,)
    )
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(notes)

@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, title, content, created_at FROM notes WHERE id = %s AND user_id = %s",
        (note_id, user_id)
    )
    note = cursor.fetchone()
    cursor.close()
    conn.close()
    if not note:
        abort(404, description="Note not found")
    return jsonify(note)

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM notes WHERE id = %s AND user_id = %s",
        (note_id, user_id)
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    if affected == 0:
        abort(404, description="Note not found")
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)