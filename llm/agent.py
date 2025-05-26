import requests

from llama import ask_groq_mistral, audio_to_text, text_to_audio

# ================== CONFIG ==================
BOT_TOKEN = "7625048712:AAG11oVb-kQv5Aj0pX2hOA-AlsPPw8L5juU"
TELE_CHAT_ID = "1666849445"  # ID người nhận hoặc group
CHAT_ID = "69e79352-17fd-4b0e-bc2b-239690b048c7"  # ID người nhận hoặc group
# ============================================

def get_file_path(file_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    response = requests.get(url)
    return response.json()

def download_file(file_path):
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    response = requests.get(url)
    with open("voice.ogg", "wb") as f:
        f.write(response.content)
    return "voice.ogg"

def send_voice(chat_id, voice_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice"
    files = {
        "voice": open(voice_path, "rb")
    }
    data = {
        "chat_id": chat_id
    }
    response = requests.post(url, files=files, data=data)
    return response.json()

# ================== CHUỖI XỬ LÝ ==================

def process_voice_reply(file_id, chat_id):
    file_info = get_file_path(file_id)
    path = file_info['result']['file_path']
    local_file = download_file(path)
    
    transcript = audio_to_text(
        file_path=local_file,
        lang="vi",
        response_format="json",
        chatid=chat_id,
        prompt="Chuyển đổi âm thanh thành văn bản",
        model_name="Whisper Large v3 Turbo"
    )
    response_text = ask_groq_mistral(
        question=transcript,
        chatid=chat_id,
        model_name="LLaMA 3.3 (70B Versatile)"
    )
    voice_bytes = text_to_audio(
        text=response_text,
        voice="Fritz-PlayAI",
        response_format="mp3",
        chatid=chat_id,
        model_name="Google Text-to-Speech"
    )
    voice_file = "response.mp3"
    with open(voice_file, "wb") as f:
        f.write(voice_bytes)
    result = send_voice(TELE_CHAT_ID, voice_file)
    return result

# ================== MAIN ==================
if __name__ == "__main__":
    # Example usage
    file_id = "AwACAgUAAxkBAAMPaCVgN2AUFloxJHf4bv7kwKeTa2MAAqkVAAIsLSlVV3jT4UeHdq02BA"
    process_voice_reply(file_id, CHAT_ID)