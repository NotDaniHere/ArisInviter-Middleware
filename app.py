import sqlite3
import bcrypt
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

DB_PATH = "LoginSecurity.db"

def verify_password(username: str, password: str) -> bool:
    """
    Connect to LoginSecurity.db, look up the bcrypt password hash for `username`,
    and compare it with the given `password`.
    Returns True if valid, otherwise False.
    """
    # 1) Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2) Fetch the stored bcrypt hash for this user
    #    Adjust the table/column if your schema differs
    cursor.execute("SELECT password FROM ls_players WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    # If user not found or password column is empty, fail immediately
    if not row:
        return False

    stored_hash = row[0]  # Should be something like "$2a$10$..."

    # 3) Compare the provided password with the stored hash using bcrypt
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))


@app.route('/invite', methods=['POST'])
def invite():
    """
    Expects JSON in the body with 'username', 'password' (the existing/registered player's credentials),
    and 'invite' (the new player to be whitelisted).
    Example:
        {
            "username": "Notch",
            "password": "mysecret123",
            "invite": "Steve"
        }
    """
    data = request.get_json()
    
    # Basic validation
    if not data or 'username' not in data or 'password' not in data or 'invite' not in data:
        return jsonify({'error': 'Missing "username", "password", or "invite" in JSON payload.'}), 400

    username = data['username']
    input_password = data['password']
    invite_user = data['invite']

    # Step 1: Verify the existing user's credentials
    if not verify_password(username, input_password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Step 2: The user is valid; proceed to invite (whitelist) the new player
    # Replace localhost/port with actual plugin host/port if needed
    plugin_url = "http://localhost:8080/whitelist"

    try:
        response = requests.post(plugin_url, json={'username': invite_user})
        
        # If the plugin responded successfully
        if response.status_code == 200:
            return jsonify({'message': f"Successfully invited '{invite_user}'!"}), 200
        else:
            # If the plugin returned an error or something unexpected
            return jsonify({'error': response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        # Handle network errors, timeouts, etc.
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Run the Flask app on port 5000 (e.g. http://127.0.0.1:5000/invite)
    app.run(port=5000, debug=True)
