from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from flask_cors import CORS
import secrets
import string

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
KEYS = {}  # Store keys with timestamps

def generate_key(length=16):
    """Generate a secure random key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@app.route("/")
def home():
    return jsonify({"message": "Key Generator Service is running"})

# Add a key (your website will call this after user completes checkpoints)
@app.route("/add_key", methods=["POST"])
def add_key():
    # If key is provided, use it; otherwise generate a new one
    key = request.json.get("key")
    if not key:
        key = generate_key()
    
    # Store the key with timestamp
    KEYS[key] = datetime.now()
    return jsonify({
        "ok": True,
        "key": key,
        "expires_at": (datetime.now() + timedelta(hours=4)).isoformat()
    })

# Check a key (your C# app will call this)
@app.route("/check_key")
def check_key():
    key = request.args.get("key")
    if key in KEYS:
        issue_time = KEYS[key]
        if datetime.now() - issue_time < timedelta(hours=4):
            return jsonify({"ok": True})
        else:
            KEYS.pop(key)
            return jsonify({"ok": False, "expired": True})
    return jsonify({"ok": False})

if __name__ == "__main__":
    print("Starting Flask server on http://localhost:5000")
    app.run(host="localhost", port=5000, debug=True)
