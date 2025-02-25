from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import json

# Загружаем переменные окружения из .env файла
load_dotenv()

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5228, debug=True)
