from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import json
import requests

# Загружаем переменные окружения из .env файла
load_dotenv()

app = Flask(__name__)

BLOB_READ_WRITE_TOKEN = os.getenv('BLOB_READ_WRITE_TOKEN')
BLOB_STORE_ID = os.getenv('BLOB_STORE_ID')

@app.route('/')
def index():
    return render_template('index.html', edit_password=os.getenv('EDIT_PASSWORD'))

@app.route('/schedule.json')
def serve_schedule():
    return app.send_static_file('schedule.json')

@app.route('/save', methods=['POST'])
def save_schedule():
    try:
        data = request.json
        # Получаем путь к файлу относительно корня проекта
        file_path = os.path.join(app.root_path, 'static', 'schedule.json')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Error saving schedule: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/blob-upload', methods=['POST'])
def handle_blob_upload():
    try:
        # 1. Генерация токена для загрузки
        auth_response = requests.post(
            "https://blob.vercel-storage.com/put",
            headers={
                "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
                "x-blob-store-id": BLOB_STORE_ID
            },
            json={
                "name": request.json.get("name"),
                "type": "application/json"
            }
        )
        
        auth_data = auth_response.json()
        
        # 2. Возвращаем данные для загрузки
        return jsonify({
            "url": auth_data['url'],
            "downloadUrl": auth_data['downloadUrl'],
            "token": auth_data['token']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5228, debug=True)
