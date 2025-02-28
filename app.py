from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
import os
from dotenv import load_dotenv
import json
import requests
import logging
from flask_cors import CORS


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)  # Включаем CORS для всех маршрутов

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

@app.route('/schedule.json')
def get_schedule():
    """Проксирует данные из публичного URL Blob Storage"""
    try:
        # Use the correct URL format (lowercase, no store_ prefix)
        store_id = BLOB_STORE_ID.replace('store_', '').lower()
        public_url = f"https://{store_id}.public.blob.vercel-storage.com/schedule.json"
        logger.info(f"Fetching from: {public_url}")
        
        try:
            response = requests.get(public_url, timeout=10)
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 404:
                logger.warning("Schedule file not found in Blob Storage")
                return jsonify({"error": "Schedule not found"}), 404
            
            if response.status_code != 200:
                logger.error(f"Error fetching schedule: {response.text}")
                return jsonify({"error": f"Failed to fetch schedule: {response.status_code}"}), 500
            
            # Пытаемся распарсить JSON
            try:
                data = response.json()
                logger.info("Successfully fetched and parsed schedule data")
                
                # Возвращаем данные напрямую с CORS заголовками
                response = jsonify(data)
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Cache-Control', 'public, max-age=300')  # кэшировать на 5 минут
                return response
                
            except Exception as e:
                logger.error(f"Error parsing JSON: {str(e)}")
                return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 500
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            return jsonify({"error": f"Network error: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in get_schedule: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

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
        
        # Используем правильный формат ID хранилища (без префикса store_ и в нижнем регистре)
        store_id = BLOB_STORE_ID.replace('store_', '').lower()
        
        try:
            # Отправляем файл напрямую через put запрос к AWS S3 вместо использования API presigned URL
            logger.info(f"Uploading directly to Vercel Blob Storage public URL: https://{store_id}.public.blob.vercel-storage.com/schedule.json")
            
            headers = {
                "Content-Type": "application/json",
                "x-content-type": "application/json",
                "x-vercel-blob-store-id": store_id,
                "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}"
            }
            
            # Прямой PUT запрос в AWS S3
            upload_response = requests.put(
                f"https://{store_id}.public.blob.vercel-storage.com/schedule.json",
                headers=headers,
                data=json_data,
                timeout=30
            )
            
            logger.info(f"Upload response status: {upload_response.status_code}")
            
            if upload_response.status_code not in [200, 201]:
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