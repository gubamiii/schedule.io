from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

app = Flask(__name__)

BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN")
BLOB_STORE_ID = os.getenv("BLOB_STORE_ID")

@app.route("/")
def index():
    return render_template("index.html", edit_password=os.getenv("EDIT_PASSWORD"))

@app.route("/api/blob-upload", methods=["POST"])
def handle_blob_upload():
    try:
        # Генерация URL для загрузки
        auth_response = requests.post(
            "https://api.vercel.com/v2/blob/upload",
            headers={
                "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "storeId": BLOB_STORE_ID,
                "contentLength": request.json.get("contentLength"),  # Длина файла в байтах
                "contentType": request.json.get("contentType"),  # MIME-тип (например, "application/json")
            },
        )

        auth_data = auth_response.json()
        print("Vercel Response:", auth_data)  # Лог для отладки

        # Проверяем, есть ли ошибка в ответе
        if "url" not in auth_data:
            return jsonify({"error": "Vercel API error", "response": auth_data}), 500

        return jsonify(auth_data)  # Возвращаем ссылку для загрузки

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5228, debug=True)