from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

app = Flask(__name__)

BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN")
BLOB_STORE_ID = os.getenv("BLOB_STORE_ID")
EDIT_PASSWORD = os.getenv("EDIT_PASSWORD")

@app.route("/")
def index():
    return render_template("index.html", edit_password=os.getenv("EDIT_PASSWORD"))

@app.route("/api/blob-upload", methods=["POST"])
def handle_blob_upload():
    try:
        auth_response = requests.post(
            "https://api.vercel.com/v2/blob/upload",
            headers={
                "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "storeId": BLOB_STORE_ID,
                "contentLength": request.json.get("contentLength"),
                "contentType": request.json.get("contentType"),
                "access": "public"  # Добавлено согласно документации
            },
        )

        auth_data = auth_response.json()
        print("Vercel Response:", auth_data)

        if "url" not in auth_data:
            return jsonify({"error": "Vercel API error", "response": auth_data}), 500

        return jsonify(auth_data)  # Возвращаем ссылку для загрузки

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/schedule.json')
def get_schedule():
    try:
        with open('static/schedule.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/verify-password', methods=['POST'])
def verify_password():
    data = request.get_json()
    password = data.get('password')

    if password == EDIT_PASSWORD:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5228, debug=True)