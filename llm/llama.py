import base64  # Import base64 for decoding
from datetime import datetime  # Import datetime for timestamps

import openai

from config import config  # Import config từ file config.py

# Validate required keys in the configuration
required_keys = ['api_key', 'api_url', 'default_model', 'models']
missing_keys = [key for key in required_keys if key not in config]
if missing_keys:
    raise KeyError(f"Missing required keys in config.json: {', '.join(missing_keys)}")

# Decode the API key from Base64
API_KEY = base64.b64decode(config['api_key']).decode('utf-8')
URL = config['api_url']
MODEL_NAME = config['default_model']
MODEL_MAP = config['models']

client = openai.OpenAI(
    api_key=API_KEY,
    base_url=URL
)

# Initialize chat history as a nested dictionary
chat_histories = {}

# Initialize chat metadata as a nested dictionary
chat_info = {}

def ask_groq_mistral(question: str, chatid: str, model_name: str = MODEL_NAME, userid: str = None) -> str:
    # Retrieve model ID based on the model name
    model_id = MODEL_MAP.get(model_name)
    if not model_id:
        return ValueError(f"Model name '{model_name}' not found.")
    
    # Initialize chat history and metadata for the user and chat ID if not present
    if userid not in chat_histories:
        chat_histories[userid] = {}
        chat_info[userid] = {}
    if chatid not in chat_histories[userid]:
        chat_histories[userid][chatid] = [
            {"role": "system", "content": "Bạn là trợ lý AI giúp người dùng trả lời các câu hỏi bằng tiếng Việt."}
        ]
        chat_info[userid][chatid] = {
            "id": chatid,
            "name": question,  # Use the first question as the chat name
            "created": datetime.now().isoformat()  # Store the creation timestamp
        }
    
    # Add user question to chat history
    chat_histories[userid][chatid].append({"role": "user", "content": question})
    
    response = client.chat.completions.create(
        model=model_id,
        messages=chat_histories[userid][chatid],
        temperature=0.3
    )
    
    # Add assistant's response to chat history
    assistant_message = response.choices[0].message.content
    chat_histories[userid][chatid].append({"role": "assistant", "content": assistant_message})
    
    return assistant_message

def audio_to_text(file_path: str, lang: str, response_format: str, chatid: str, prompt: str, model_name: str = MODEL_NAME, userid: str = None) -> str:
    # Lấy model ID từ tên mô hình
    model_id = MODEL_MAP.get(model_name)
    if not model_id:
        raise ValueError(f"Model name '{model_name}' not found.")

    # Initialize chat history for the user and chat ID if not present
    if userid not in chat_histories:
        chat_histories[userid] = {}
        chat_info[userid] = {}
    if chatid not in chat_histories[userid]:
        chat_histories[userid][chatid] = [
            {"role": "system", "content": "Bạn là trợ lý AI giúp người dùng chuyển đổi âm thanh thành văn bản."}
        ]
        chat_info[userid][chatid] = {
            "id": chatid,
            "name": prompt,  # Use the file path as the chat name
            "created": datetime.now().isoformat()  # Store the creation timestamp
        }

    # Add prompt (if provided) to chat history
    if prompt:
        chat_histories[userid][chatid].append({"role": "user", "content": f"Prompt: {prompt}"})

    try:
        with open(file_path, "rb") as file:
            response = client.audio.transcriptions.create(
                file=file,
                model=model_id,
                response_format=response_format,
                language=lang,
                temperature=0,
                prompt=prompt  # Include the prompt parameter
            )
            transcription = response.text  # Access the 'text' attribute instead of subscript notation

            # Add transcription result to chat history
            chat_histories[userid][chatid].append({"role": "assistant", "content": transcription})

            return transcription
        
    except Exception as e:
        # Xử lý lỗi từ API
        raise Exception(f"Error during audio-to-text conversion: {str(e)}")

def text_to_audio(text: str, voice: str, response_format: str, chatid: str, model_name: str = MODEL_NAME, userid: str = None) -> bytes:
    # Retrieve model ID based on the model name
    model_id = MODEL_MAP.get(model_name)
    if not model_id:
        raise ValueError(f"Model name '{model_name}' not found.")
    
    if userid not in chat_histories:
        chat_histories[userid] = {}
        chat_info[userid] = {}

    prompt = f"Chuyen chuoi sau thanh am thanh: {text}"  # Use the text as the prompt for the chat name
    if chatid not in chat_histories[userid]:
        chat_histories[userid][chatid] = [
            {"role": "system", "content": "Bạn là trợ lý AI giúp người dùng chuyển đổi âm thanh thành văn bản."}
        ]
        chat_info[userid][chatid] = {
            "id": chatid,
            "name": prompt,  # Use the file path as the chat name
            "created": datetime.now().isoformat()  # Store the creation timestamp
        }

    # Add prompt (if provided) to chat history
    if prompt:
        chat_histories[userid][chatid].append({"role": "user", "content": prompt})
        chat_histories[userid][chatid].append({"role": "assistant", "content": "Đã chuyển đổi văn bản thành âm thanh."})

    try:
        response = client.audio.speech.create(
            input=text,
            model=model_id,
            voice=voice,
            response_format=response_format,
        )
        return response.content  # Return the binary audio data
    except Exception as e:
        raise Exception(f"Error during text-to-audio conversion: {str(e)}")
    

# Giao diện hỏi đáp đơn giản
# while True:
#     q = input("Nhập câu hỏi của bạn (hoặc 'exit' để thoát): ")
#     if q.lower() == "exit":
#         break
#     answer = ask_groq_mistral(q)
#     print("Trả lời:", answer)
