from functools import wraps
from quart import request, jsonify
import jwt

def token_required(func):
    @wraps(func)
    async def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token is missing or invalid"}), 401

        token = auth_header.split(' ')[1]
        
        try:
            decoded_token = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
            request.user_id = decoded_token.get('user_id')
            print(f'User ID: {request.user_id}')
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return await func(*args, **kwargs)
    return decorated