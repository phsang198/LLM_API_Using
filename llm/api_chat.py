from llm.llama import chat_histories, chat_info

def get_chat_ids(userid):
    if userid is None or userid not in chat_histories:
        return []
    # Retrieve chat IDs for the specified user
    return list(chat_histories[userid].keys())

def get_chat_metadata(userid):
    if userid is None or userid not in chat_histories:
        return []
    # Return metadata for the specified chat
    return list(chat_info[userid].values())

def get_chat_history(userid, chatid):
    if userid is None or userid not in chat_histories:
        return "User ID not found."
    if chatid is None or chatid not in chat_histories[userid]:
        return "Chat ID not found."
    # Check if the user and chat ID exist in the chat histories
    if userid in chat_histories and chatid in chat_histories[userid]:
        return chat_histories[userid][chatid]
    
    return "No chat history found."

def clear_chat_history(userid):
    # Clear chat history and metadata for the specified user
    if userid in chat_histories:
        del chat_histories[userid]
    if userid in chat_info:
        del chat_info[userid]
    return "Chat history cleared."
