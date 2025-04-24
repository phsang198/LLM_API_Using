import json  # Import thêm module json để đọc config
import threading

from flask import Flask, jsonify, request

from llama import ask_groq_mistral

#import time  # Import thêm module time để đo thời gian



app = Flask(__name__)

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def process_question(question, model_name, result_dict, thread_id):
    try:
        #start_time = time.time()  # Bắt đầu đo thời gian
        result_dict[thread_id] = ask_groq_mistral(question, model_name=model_name)
        #end_time = time.time()  # Kết thúc đo thời gian
        #print(f"Thread {thread_id}: Processing question took {end_time - start_time:.4f} seconds")
    except Exception as e:
        result_dict[thread_id] = str(e)

@app.route('/api/ask', methods=['POST'])
def ask_api():
    #start_time = time.time()  # Bắt đầu đo thời gian toàn bộ API
    data = request.get_json()
    if not data or 'text' not in data or 'model_name' not in data:
        return jsonify({'error': 'Invalid input, expected JSON with "text" and "model_name" fields.'}), 400

    questions = data['text'] if isinstance(data['text'], list) else [data['text']]
    model_name = data['model_name']
    threads = []
    results = {}

    # Đo thời gian tạo và chạy các thread
    #thread_start_time = time.time()
    for i, question in enumerate(questions):
        thread = threading.Thread(target=process_question, args=(question, model_name, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    #thread_end_time = time.time()
    #print(f"Thread execution took {thread_end_time - thread_start_time:.4f} seconds")

    #end_time = time.time()  # Kết thúc đo thời gian toàn bộ API
    #print(f"Total API execution time: {end_time - start_time:.4f} seconds")

    #return jsonify({'results': [results[i] for i in range(len(questions))]})
    return results[0]

if __name__ == '__main__':
    app.run(debug=False, host=config['host'], port=config['port'])