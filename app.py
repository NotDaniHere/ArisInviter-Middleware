import sqlite3
import bcrypt
from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__, static_folder = 'static')
DB_PATH = "./plugins/LoginSecurity/LoginSecurity.db"

def verify_password(username: str, password: str) -> bool:
    """
    Connect to LoginSecurity.db, look up the bcrypt password hash for the row
    where last_name == `username`, and compare it with the given `password`.
    Returns True if valid, otherwise False.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM ls_players WHERE last_name = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    # If user not found or password column is empty, fail immediately
    if not row:
        return False

    stored_hash = row[0]  # Should be something like "$2a$10$..."

    # 3) Compare the provided password with the stored hash using bcrypt
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/invite', methods=['POST'])
def invite():
    """
    Expects JSON in the body with:
      - 'username': The existing player's in-game name (stored in `last_name`)
      - 'password': The existing player's password (bcrypt)
      - 'invite':   The new player to be whitelisted
    Example body:
        {
            "username": "Notch",
            "password": "mysecret123",
            "invite":   "Steve"
        }
    """
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data or 'invite' not in data:
        return jsonify({'error': 'Missing "username", "password", or "invite" in JSON payload.'}), 400

    username = data['username']
    input_password = data['password']
    invite_user = data['invite']

    if not verify_password(username, input_password):
        return jsonify({'error': 'Invalid username or password'}), 401

    plugin_url = "http://localhost:8080/whitelist"

    try:
        response = requests.post(plugin_url, json={'username': invite_user})
        if response.status_code == 200:
            return jsonify({'message': f"Successfully invited '{invite_user}'!"}), 200
        else:
            return jsonify({'error': response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
