import os  # Import thêm module os để xử lý file
import threading
import uuid  # Import thêm module uuid để tạo tên file duy nhất
from uuid import UUID  # Import UUID for validation

from flask import Flask, jsonify, request

from authen import get_userid_from_token
from config import config  # Import config từ file config.py
from conversation import conversation_bp
from llm.api_audio import text_2_audio
from llm.llama import ask_groq_mistral, audio_to_text, text_to_audio

#from waitress import serve

app = Flask(__name__)

# Register the conversation blueprint
app.register_blueprint(conversation_bp)
    
def process_question(question, model_name, result_dict, thread_id, chat_id, userid):
    try:
        result_dict[thread_id] = ask_groq_mistral(question, chatid=chat_id, model_name=model_name, userid=userid)
    except Exception as e:
        result_dict[thread_id] = str(e)

@app.route('/api/chat', methods=['POST'])
def ask_api():
    token = request.headers.get('token')
    if token is None:
        userid = None
    else:
        userid = get_userid_from_token(token)

        try:
            UUID(str(userid))  # Validate if userid is a valid UUID
        except ValueError:
            return jsonify({'error': 'Invalid userid format.'}), 401

    data = request.get_json()
    if not data or 'prompt' not in data or 'model_name' not in data:
        return jsonify({'error': 'Invalid input, expected JSON with "prompt" and "model_name" fields.'}), 400

    questions = data['prompt'] if isinstance(data['prompt'], list) else [data['prompt']]
    model_name = data['model_name']
    chat_id = data.get('chat_id', str(uuid.uuid4()))  # Generate new UUID if chat_id is not provided
    threads = []
    results = {}

    for i, question in enumerate(questions):
        thread = threading.Thread(target=process_question, args=(question, model_name, results, i, chat_id, userid))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return jsonify(results)

@app.route('/api/audio/stt', methods=['POST'])
def audio_stt_api():
    token = request.headers.get('token')
    if token is None:
        userid = None
    else:
        userid = get_userid_from_token(token)

        try:
            UUID(str(userid))  # Validate if userid is a valid UUID
        except ValueError:
            return jsonify({'error': 'Invalid userid format.'}), 401

    if 'file' not in request.files or 'language' not in request.form or 'response_format' not in request.form:
        return jsonify({'error': 'Invalid input, expected multipart with "file", "language", "response_format".'}), 400

    file = request.files['file']
    lang = request.form['language']
    response_format = request.form['response_format']
    chat_id = request.form.get('chat_id', str(uuid.uuid4()))  # Generate new UUID if chat_id is not provided
    model_name = request.form.get('model_name', config['default_model'])
    prompt = request.form.get('prompt') 
    if prompt is None:
        prompt = "Chuyển audio thành text"
    if not file or file.filename == '':
        return jsonify({'error': 'No file provided.'}), 400

    try:
        cache_dir = "cache"
        os.makedirs(cache_dir, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(cache_dir, unique_filename)
        file.save(file_path)

        result = audio_to_text(file_path, lang, response_format, chat_id, prompt, model_name=model_name, userid=userid)
        return jsonify({'text': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

@app.route('/api/audio/tts', methods=['POST'])
def audio_tts_api():
    token = request.headers.get('token')
    if token is None:
        userid = None
    else:
        userid = get_userid_from_token(token)

        try:
            UUID(str(userid))  # Validate if userid is a valid UUID
        except ValueError:
            return jsonify({'error': 'Invalid userid format.'}), 401

    data = request.get_json()
    if not data or 'model_name' not in data or 'input' not in data or 'language' not in data or 'voice' not in data or 'response_format' not in data:
        return jsonify({'error': 'Invalid input, expected JSON with "model_name", "input", "language", "voice", "response_format", and optionally "chat_id".'}), 400

    model_name = data['model_name']
    text_input = data['input']
    language = data['language']
    voice = data['voice']
    response_format = data['response_format']
    chat_id = data.get('chat_id', str(uuid.uuid4()))  # Generate new UUID if chat_id is not provided

    try:
        if model_name == "Playai Text Speed":
            result = text_to_audio(text_input, voice, response_format, chat_id, model_name=model_name, userid=userid)
        elif model_name == "Google Text-to-Speech":
            if response_format != "mp3":
                return jsonify({'error': 'Google TTS only supports mp3 format.'}), 400
            result = text_2_audio(text_input, response_format, language, chat_id, userid=userid)
        #Save the result to a file in the cache folder
        # cache_dir = "cache"
        # os.makedirs(cache_dir, exist_ok=True)
        # unique_filename = f"{uuid.uuid4()}.{response_format}"
        # file_path = os.path.join(cache_dir, unique_filename)
        # with open(file_path, 'wb') as f:
        #     f.write(result)

        return result, 200, {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': f'attachment; filename="{uuid.uuid4()}.{response_format}"'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host=config['host'], port=config['port'])
    #serve(app, host=config['host'], port=config['port'])