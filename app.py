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
    data = request.json
    # Здесь нужно добавить сохранение в файл
    with open('static/schedule.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5228, debug=True)
