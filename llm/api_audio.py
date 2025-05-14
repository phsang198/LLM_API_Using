import io
from datetime import datetime

from gtts import gTTS

from llm.llama import chat_histories, chat_info

# from pydub import AudioSegment



def text_2_audio(text: str, response_format: str, language: str, chatid: str, userid:str = None) -> bytes:

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
        tts = gTTS(text=text, lang=language)
        audio_data = io.BytesIO()
        tts.write_to_fp(audio_data)
        audio_data.seek(0)

        if response_format == 'mp3':
            return audio_data.read()
        # else:
        #     # Convert from mp3 in memory to requested format
        #     audio = AudioSegment.from_file(audio_data, format="mp3")
        #     output_data = io.BytesIO()
        #     audio.export(output_data, format=response_format)
        #     output_data.seek(0)
        #     return output_data.read()

    except Exception as e:
        raise Exception(f"Lỗi chuyển văn bản thành giọng nói: {str(e)}")