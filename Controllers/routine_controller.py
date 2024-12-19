from quart import request, jsonify
import jwt
from .auth_token.middleware import token_required

class RoutineController:
    def __init__(self, app, routine_service):
        self.app = app
        self.routine_service = routine_service
        self.register_endpoints()

    def register_endpoints(self):
        @self.app.route('/api/setroutine', methods=['POST'])
        @token_required
        async def set_routine():
            if not request.is_json:
                return jsonify({"error": "Request must be in JSON format"}), 400

            data = await request.get_json()
            if 'hours' not in data or 'selectedDays' not in data:
                return jsonify({"error": "Missing 'hours' or 'selectedDays' in request"}), 400

            hours = data['hours']
            selectedDays = data['selectedDays']

            try:
                await self.routine_service.manage_routine(request.user_id, selectedDays, hours)
                return jsonify({"message": "Routine set successfully"}), 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/getroutine', methods=['GET'])
        @token_required
        async def get_routine():
            try:
                routine = await self.routine_service.get_routine(request.user_id)
                return jsonify({"message": "Routine retrieved successfully", "routine": routine}), 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500