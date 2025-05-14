from uuid import UUID

from flask import Blueprint, jsonify, request

from authen import get_userid_from_token
from llm.api_chat import (clear_chat_history, get_chat_history,
                          get_chat_metadata)

conversation_bp = Blueprint('conversation', __name__)

@conversation_bp.route('/api/conversation/metadata', methods=['GET'])
def get_chat_history_api():
    token = request.headers.get('token')
    if token is None:
        userid = None
    else:
        userid = get_userid_from_token(token)

        try:
            UUID(str(userid))  # Validate if userid is a valid UUID
        except ValueError:
            return jsonify({'error': 'Invalid userid format.'}), 401

    chat_id = request.args.get('chat_id')

    if not chat_id:
        return jsonify({'error': 'chat_id not found.'}), 400

    history = get_chat_history(userid, chat_id)
    if isinstance(history, str):  # Check if the result is a string
        return jsonify({'error': history}), 400
    return jsonify({'chat_history': history})

@conversation_bp.route('/api/conversation/list', methods=['GET'])
def get_chat_ids_api():
    token = request.headers.get('token')
    if token is None:
        userid = None
    else:
        userid = get_userid_from_token(token)

        try:
            UUID(str(userid))  # Validate if userid is a valid UUID
        except ValueError:
            return jsonify({'error': 'Invalid userid format.'}), 401

    chat_ids = get_chat_metadata(userid) if userid else []
    return jsonify({'chat_list': chat_ids})

@conversation_bp.route('/api/conversation/clear', methods=['DELETE'])
def clear_chat_history_api():
    token = request.headers.get('token')
    if token is None:
        return jsonify({'error': 'Token not provided.'}), 401
    else:
        userid = get_userid_from_token(token)

        try:
            UUID(str(userid))  # Validate if userid is a valid UUID
        except ValueError:
            return jsonify({'error': 'Invalid userid format.'}), 401

    result = clear_chat_history(userid)
    return jsonify({'result': result})