from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import json
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN")
BLOB_STORE_ID = os.getenv("BLOB_STORE_ID")
EDIT_PASSWORD = os.getenv("EDIT_PASSWORD")

logger.info(f"BLOB_STORE_ID set: {bool(BLOB_STORE_ID)}")
logger.info(f"BLOB_READ_WRITE_TOKEN set: {bool(BLOB_READ_WRITE_TOKEN)}")
logger.info(f"EDIT_PASSWORD set: {bool(EDIT_PASSWORD)}")


@app.route("/")
def index():
    # Передаем переменные окружения в шаблон
    return render_template("index.html", 
                          edit_password=EDIT_PASSWORD,
                          blob_store_id=BLOB_STORE_ID,
                          env_info={
                              "BLOB_STORE_ID": bool(BLOB_STORE_ID),
                              "BLOB_READ_WRITE_TOKEN": bool(BLOB_READ_WRITE_TOKEN),
                              "EDIT_PASSWORD": bool(EDIT_PASSWORD)
                          })

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
        logger.info("Fetching schedule from Vercel Blob Storage")
        
        # Проверяем, что переменные окружения установлены
        if not BLOB_READ_WRITE_TOKEN:
            logger.error("BLOB_READ_WRITE_TOKEN is not set")
             
            
        if not BLOB_STORE_ID:
            logger.error("BLOB_STORE_ID is not set")
             
        
        # Get the file from Vercel Blob Storage
        headers = {
            "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}"
        }
        
        blob_url = f"https://blob.vercel-storage.com/{BLOB_STORE_ID}/schedule.json"
        logger.info(f"Blob URL: {blob_url}")
        
        try:
            response = requests.get(
                blob_url,
                headers=headers,
                timeout=10  # Добавляем таймаут
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 404:
                logger.warning("Schedule file not found, returning default schedule")
                 
            
            if response.status_code != 200:
                logger.error(f"Error fetching schedule: {response.text}")
                logger.error(f"Response headers: {dict(response.headers)}")
                # Возвращаем базовое расписание вместо ошибки
                 
            
            # Parse the JSON from the response
            try:
                data = response.json()
                logger.info(f"Successfully parsed JSON data with keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                
                # Если данные пусты, возвращаем базовое расписание
                if not data or (isinstance(data, dict) and len(data) == 0):
                    logger.warning("Empty schedule data, returning default schedule")
                     
                    
                # Return the data directly
                return jsonify(data)
                
            except Exception as e:
                logger.error(f"Error parsing JSON: {str(e)}")
                logger.error(f"Response content: {response.text[:200]}...")
                 
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
             
            
    except Exception as e:
        logger.error(f"Unexpected error in get_schedule: {str(e)}")
        # В случае любой ошибки возвращаем базовое расписание
         

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
            logger.warning("Invalid password attempt in save_schedule")
            return jsonify({"error": "Invalid password"}), 403
            
        schedule_data = data.get('schedule')
        if not schedule_data:
            logger.error("No schedule data provided")
            return jsonify({"error": "No schedule data provided"}), 400
            
        # Проверяем, что переменные окружения установлены
        if not BLOB_READ_WRITE_TOKEN:
            logger.error("BLOB_READ_WRITE_TOKEN is not set")
            return jsonify({"error": "Storage configuration error"}), 500
            
        if not BLOB_STORE_ID:
            logger.error("BLOB_STORE_ID is not set")
            return jsonify({"error": "Storage configuration error"}), 500
            
        # Convert data to JSON string and encode to bytes
        json_data = json.dumps(schedule_data).encode()
        
        # Create a request to Vercel Blob API
        headers = {
            "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}"
        }
        
        try:
            # Get a presigned URL
            logger.info("Getting presigned URL for upload")
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
                },
                timeout=10
            )
            
            if presigned_url_response.status_code != 200:
                logger.error(f"Failed to get presigned URL: {presigned_url_response.status_code} - {presigned_url_response.text}")
                return jsonify({"error": "Failed to get upload URL"}), 500
            
            presigned_data = presigned_url_response.json()
            
            if "url" not in presigned_data:
                logger.error(f"URL not found in presigned data: {presigned_data}")
                return jsonify({"error": "Failed to get upload URL"}), 500
            
            # Upload the file to the presigned URL
            logger.info(f"Uploading file to presigned URL: {presigned_data['url']}")
            upload_response = requests.put(
                presigned_data["url"],
                data=json_data,
                headers={
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            
            if upload_response.status_code != 200:
                logger.error(f"Failed to upload file: {upload_response.status_code} - {upload_response.text}")
                return jsonify({"error": "Failed to upload file"}), 500
                
            logger.info("Schedule successfully saved")
            return jsonify({"success": True}), 200
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception during save: {str(e)}")
            return jsonify({"error": f"Network error: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in save_schedule: {str(e)}")
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