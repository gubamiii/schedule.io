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
        print("Fetching schedule from Vercel Blob Storage")
        # Get the file from Vercel Blob Storage
        headers = {
            "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}"
        }
        
        blob_url = f"https://blob.vercel-storage.com/{BLOB_STORE_ID}/schedule.json"
        print(f"Blob URL: {blob_url}")
        
        response = requests.get(
            blob_url,
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 404:
            print("Schedule file not found, returning empty object")
            # Return empty schedule if file doesn't exist
            return jsonify({})
        
        if response.status_code != 200:
            print(f"Error fetching schedule: {response.text}")
            return jsonify({"error": "Failed to fetch schedule"}), 500
        
        # Parse the JSON from the response
        try:
            data = response.json()
            print(f"Successfully parsed JSON data with keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
        except Exception as e:
            print(f"Error parsing JSON: {str(e)}")
            print(f"Response content: {response.text[:200]}...")
            return jsonify({"error": f"Failed to parse schedule data: {str(e)}"}), 500
        
        # Return the data directly
        return jsonify(data)
    except Exception as e:
        print(f"Unexpected error in get_schedule: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/verify-password', methods=['POST'])
def verify_password():
    data = request.get_json()
    password = data.get('password')

    if password == EDIT_PASSWORD:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 403

@app.route('/api/save-schedule', methods=['POST'])
def save_schedule():
    try:
        data = request.get_json()
        
        # Verify the edit password
        password = data.get('password')
        if password != EDIT_PASSWORD:
            return jsonify({"error": "Invalid password"}), 403
            
        schedule_data = data.get('schedule')
        if not schedule_data:
            return jsonify({"error": "No schedule data provided"}), 400
            
        # Convert data to JSON string and encode to bytes
        json_data = json.dumps(schedule_data).encode()
        
        # Create a request to Vercel Blob API
        headers = {
            "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}"
        }
        
        # Get a presigned URL
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
            return jsonify({"error": "Failed to get presigned URL"}), 500
        
        # Upload the file to the presigned URL
        upload_response = requests.put(
            presigned_data["url"],
            data=json_data,
            headers={
                "Content-Type": "application/json"
            }
        )
        
        if upload_response.status_code != 200:
            return jsonify({"error": "Failed to upload file"}), 500
            
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/check-blob-config')
def check_blob_config():
    try:
        # Check if environment variables are set
        config = {
            "BLOB_STORE_ID": BLOB_STORE_ID is not None,
            "BLOB_READ_WRITE_TOKEN": BLOB_READ_WRITE_TOKEN is not None,
            "EDIT_PASSWORD": EDIT_PASSWORD is not None
        }
        
        # Try to list blobs to verify token works
        if BLOB_READ_WRITE_TOKEN and BLOB_STORE_ID:
            headers = {
                "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}"
            }
            
            response = requests.get(
                f"https://blob.vercel-storage.com/list?storeId={BLOB_STORE_ID}",
                headers=headers
            )
            
            config["blob_list_status"] = response.status_code
            
            if response.status_code == 200:
                blob_data = response.json()
                config["blobs"] = blob_data.get("blobs", [])
                config["status"] = "success"
            else:
                config["error"] = response.text
                config["status"] = "error"
        else:
            config["status"] = "missing_config"
            
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e), "status": "exception"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5228, debug=True)