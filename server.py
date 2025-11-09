from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import secrets
import string
import os

app = Flask(__name__)

# Database setup (SQLite in Railway)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///keys.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Key model
class Key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Generate secure random key
def generate_key(length=30):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
def home():
    return jsonify({"message": "Key Generator Service is running"})

# Add a new key (your website calls after checkpoints)
@app.route("/add_key", methods=["POST"])
def add_key():
    key_value = request.json.get("key")
    if not key_value:
        key_value = generate_key()

    # Ensure unique
    while Key.query.filter_by(key=key_value).first():
        key_value = generate_key()

    new_key = Key(key=key_value)
    db.session.add(new_key)
    db.session.commit()

    expires_at = datetime.utcnow() + timedelta(hours=4)
    return jsonify({"ok": True, "key": key_value, "expires_at": expires_at.isoformat()})

# Check key (your C# app calls this)
@app.route("/check_key")
def check_key():
    key_value = request.args.get("key")
    if not key_value:
        return jsonify({"ok": False, "error": "No key provided"})

    key_entry = Key.query.filter_by(key=key_value).first()
    if key_entry:
        if datetime.utcnow() - key_entry.created_at < timedelta(hours=4):
            return jsonify({"ok": True})
        else:
            db.session.delete(key_entry)
            db.session.commit()
            return jsonify({"ok": False, "expired": True})
    return jsonify({"ok": False})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask server on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
