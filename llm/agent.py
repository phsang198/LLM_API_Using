import os

from llm.llama import ask_groq_mistral, audio_to_text, text_to_audio


def process_input(input_data, lang='vi', response_format='text', chatid='default_chat', userid='default_user'):
    is_audio_response = False  # Flag to determine if the response should be audio

    if os.path.isfile(input_data):
        # If input is a file, process it as audio
        transcription = audio_to_text(
            file_path=input_data,
            lang=lang,
            response_format=response_format,
            chatid=chatid,
            prompt="Transcribe this audio",
            userid=userid
        )
        input_text = transcription
    else:
        # If input is a string, use it directly
        input_text = input_data

    # Analyze the input text for specific requests
    if "trả lời tôi bằng âm thanh" in input_text.lower():
        is_audio_response = True
        response_text = "Tôi sẽ trả lời bạn bằng âm thanh từ bây giờ."
    else:
        # Use the ask_groq_mistral function to get a response
        response_text = ask_groq_mistral(
            question=input_text,
            chatid=chatid,
            userid=userid
        )

    # Return the response in the requested format
    if is_audio_response:
        audio_response = text_to_audio(
            text=response_text,
            voice="default",
            response_format="audio",
            chatid=chatid,
            userid=userid
        )
        return {"type": "audio", "result": audio_response}
    else:
        return {"type": "text", "result": response_text}