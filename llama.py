import json

import openai

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Validate required keys in the configuration
required_keys = ['api_key', 'api_url', 'default_model', 'models']
missing_keys = [key for key in required_keys if key not in config]
if missing_keys:
    raise KeyError(f"Missing required keys in config.json: {', '.join(missing_keys)}")

API_KEY = config['api_key']
URL = config['api_url']
MODEL_NAME = config['default_model']
MODEL_MAP = config['models']

client = openai.OpenAI(
    api_key=API_KEY,
    base_url=URL
)

def ask_groq_mistral(question: str, model_name: str = MODEL_NAME) -> str:
    # Retrieve model ID based on the model name
    model_id = MODEL_MAP.get(model_name)
    if not model_id:
        return ValueError(f"Model name '{model_name}' not found.")
    
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "Bạn là trợ lý AI giúp người dùng trả lời các câu hỏi bằng tiếng Việt."},
            {"role": "user", "content": question}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

def audio_to_text(file_path: str, lang: str, response_format: str, model_name: str = MODEL_NAME) -> str:
    
    # Lấy model ID từ tên mô hình
    model_id = MODEL_MAP.get(model_name)
    if not model_id:
        raise ValueError(f"Model name '{model_name}' not found.")

    try:
        with open(file_path, "rb") as file:
            response = client.audio.transcriptions.create(
                file=file,
                model=model_id,
                response_format=response_format,
                language=lang,
                temperature=0
            )
            return response.text  # Access the 'text' attribute instead of subscript notation
        
    except Exception as e:
        # Xử lý lỗi từ API
        raise Exception(f"Error during audio-to-text conversion: {str(e)}")
    
# Giao diện hỏi đáp đơn giản
# while True:
#     q = input("Nhập câu hỏi của bạn (hoặc 'exit' để thoát): ")
#     if q.lower() == "exit":
#         break
#     answer = ask_groq_mistral(q)
#     print("Trả lời:", answer)
