from app.data.db import connect_database 

def get_user_by_username(username):
    """Retrieve user by username."""
    conn = connect_database()

    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE username = ?"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()   
        return user
    finally:
            conn.close()

def insert_user(username, password_hash, role="user"):
    """Insert new user."""
    conn = connect_database()
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
        cursor.execute(sql, (username, password_hash, role))
        conn.commit()
    finally:
        conn.close()

