#!/usr/bin/env python3
"""URL shortener — Flask API with SQLite backend."""
import hashlib
import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)
DB = os.environ.get("DB_PATH", "urls.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                clicks INTEGER DEFAULT 0
            )
        """)

def generate_short_code(url: str) -> str:
    hash_bytes = hashlib.sha256(url.encode()).digest()
    return hash_bytes[:4].hex()[:7]

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' field"}), 400
    
    url = data["url"]
    custom_code = data.get("code")
    
    short_code = custom_code or generate_short_code(url + str(datetime.now()))
    
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO urls (short_code, original_url, created_at) VALUES (?, ?, ?)",
                (short_code, url, datetime.now().isoformat()),
            )
        return jsonify({
            "short_url": f"{request.host_url}{short_code}",
            "original_url": url,
            "code": short_code,
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Code already exists"}), 409

@app.route("/<code>")
def redirect_url(code):
    with get_db() as conn:
        row = conn.execute("SELECT original_url FROM urls WHERE short_code = ?", (code,)).fetchone()
        if row:
            conn.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (code,))
            return redirect(row["original_url"])
    return jsonify({"error": "Not found"}), 404

@app.route("/stats/<code>")
def stats(code):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM urls WHERE short_code = ?", (code,)).fetchone()
        if row:
            return jsonify(dict(row))
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
