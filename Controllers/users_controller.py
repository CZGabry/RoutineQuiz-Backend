from quart import request, jsonify
import jwt
import datetime
from quart import request, jsonify
from Services.user_service import UserService
from .auth_token.middleware import token_required

class UserController:
    def __init__(self, app, user_service):
        self.app = app
        self.user_service = user_service
        self.register_endpoints()

    def register_endpoints(self):
        @self.app.route('/api/register', methods=['POST'])
        async def register():
            data = await request.get_json()
            result, message = await self.user_service.register_user(
                data.get('username'), data.get('password'), data.get('email'))
            if result:
                return jsonify({"status": "Success", "message": message}), 200
            else:
                return jsonify({"error": message}), 409

        @self.app.route('/api/login', methods=['POST'])
        async def login():
            data = await request.get_json()
            is_valid, user_id = await self.user_service.login_user(
                data.get('identifier'), data.get('password'), data.get('device_token'))
            if is_valid:
                token = jwt.encode({
                    'user_id': user_id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                }, 'your_secret_key', algorithm='HS256')
                username = await self.user_service.user_repository.get_username_by_id(user_id)
                return jsonify({"status": "Success", "message": "Login successful", "token": token, "username": username}), 200
            else:
                return jsonify({"error": "Invalid login credentials"}), 401
