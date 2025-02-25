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
    return render_template("index.html")

@app.route("/api/blob-upload", methods=["POST"])
def handle_blob_upload():
    try:
        # Get the data from the request
        data = request.json.get("data")
        
        # Convert data to JSON string and encode to bytes
        json_data = json.dumps(data).encode()
        
        # Create a multipart form-data request to Vercel Blob API
        headers = {
            "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}"
        }
        
        # First, get a presigned URL
        presigned_url_response = requests.post(
            "https://blob.vercel-storage.com/post-url",
            headers=headers,
            json={
                "size": len(json_data),
                "contentType": "application/json",
                "storeId": BLOB_STORE_ID,
                "pathname": "schedule.json",
                "access": "public",
                "addRandomSuffix": False
            }
        )
        
        presigned_data = presigned_url_response.json()
        
        if "url" not in presigned_data:
            return jsonify({"error": "Failed to get presigned URL", "response": presigned_data}), 500
        
        # Now upload the file to the presigned URL
        upload_response = requests.put(
            presigned_data["url"],
            data=json_data,
            headers={
                "Content-Type": "application/json"
            }
        )
        
        if upload_response.status_code != 200:
            return jsonify({"error": "Failed to upload file", "status": upload_response.status_code}), 500
        
        # Return the URL where the file can be accessed
        return jsonify({
            "url": presigned_data["url"],
            "downloadUrl": f"https://blob.vercel-storage.com/{BLOB_STORE_ID}/schedule.json"
        })
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