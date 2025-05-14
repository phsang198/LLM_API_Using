import json  # Import thêm module json để parse authorization

import jwt  # Import thêm module jwt để xử lý token

from config import config  # Import config từ file config.py


def get_userid_from_token(token):
    try:
        decoded = jwt.decode(token, config['secretkey'], algorithms=["HS256"])
        # Parse 'authorization' as JSON and extract 'user'
        authorization = json.loads(decoded.get('authorization', '[]'))
        if isinstance(authorization, list) and len(authorization) > 0:
            return authorization[0].get('userid')
        return 'Invalid token structure'
    except Exception as e:
        print(f"Error decoding token: {e}")
        return 'Invalid token'