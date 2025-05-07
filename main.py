import json  # Import thêm module json để đọc config
import os  # Import thêm module os để xử lý file
import threading
import uuid  # Import thêm module uuid để tạo tên file duy nhất

from flask import Flask, jsonify, request

from llama import ask_groq_mistral, audio_to_text

from waitress import serve

app = Flask(__name__)

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def process_question(question, model_name, result_dict, thread_id):
    try:
        result_dict[thread_id] = ask_groq_mistral(question, model_name=model_name)
    except Exception as e:
        result_dict[thread_id] = str(e)

@app.route('/api/ask', methods=['POST'])
def ask_api():

    data = request.get_json()
    if not data or 'text' not in data or 'model_name' not in data:
        return jsonify({'error': 'Invalid input, expected JSON with "text" and "model_name" fields.'}), 400

    questions = data['text'] if isinstance(data['text'], list) else [data['text']]
    model_name = data['model_name']
    threads = []
    results = {}

    for i, question in enumerate(questions):
        thread = threading.Thread(target=process_question, args=(question, model_name, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results[0]

@app.route('/api/audio', methods=['POST'])
def audio_api():
    if 'file' not in request.files or 'language' not in request.form or 'response_format' not in request.form:
        return jsonify({'error': 'Invalid input, expected multipart with "file", "language", and "response_format".'}), 400

    file = request.files['file']
    lang = request.form['language']  # Changed from 'lang' to 'language'
    response_format = request.form['response_format']
    model_name = request.form.get('model_name', config['default_model'])

    if not file or file.filename == '':
        return jsonify({'error': 'No file provided.'}), 400

    try:
        cache_dir = "cache"
        os.makedirs(cache_dir, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}_{file.filename}"  # Tạo tên file duy nhất
        file_path = os.path.join(cache_dir, unique_filename)
        file.save(file_path)  # Lưu file xuống cache

        result = audio_to_text(file_path, lang, response_format, model_name)
        return jsonify({'text': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)  # Xóa file sau khi xử lý

if __name__ == '__main__':
    app.run(debug=False, host=config['host'], port=config['port'])
    #serve(app, host=config['host'], port=config['port'])