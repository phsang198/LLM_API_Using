#import time
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

# Giao diện hỏi đáp đơn giản
# while True:
#     q = input("Nhập câu hỏi của bạn (hoặc 'exit' để thoát): ")
#     if q.lower() == "exit":
#         break
#     answer = ask_groq_mistral(q)
#     print("Trả lời:", answer)
