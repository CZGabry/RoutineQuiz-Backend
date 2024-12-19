from quart import Quart, request, jsonify
import jwt
from .auth_token.middleware import token_required

class QuizController:
    def __init__(self, app, quiz_service):
        self.app = app
        self.quiz_service = quiz_service
        self.register_endpoints()

    def register_endpoints(self):
        @self.app.route('/api/upload_note', methods=['POST'])
        @token_required
        async def upload_quiz():
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400

            data = await request.get_json()
            sentence = data.get('text')
            number_of_questions = data.get('number_of_questions')

            try:
                quiz_array, topic = await self.quiz_service.handle_quiz_creation(request.user_id, sentence, number_of_questions)
                return jsonify({"status": "Success", "message": "Quiz uploaded successfully", "topic": topic}), 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/quizzes_by_set/<int:set_id>', methods=['GET'])
        @token_required
        async def get_quizzes(set_id):
            quizzes = await self.quiz_service.fetch_quizzes(request.user_id, set_id)
            if not quizzes:
                return jsonify({"error": "No quizzes found for the specified set"}), 404

            return jsonify({"status": "Success", "quizzes": quizzes}), 200

        @self.app.route('/api/delete_quiz/<int:set_id>', methods=['DELETE'])
        @token_required
        async def delete_quizzes(set_id):
            try:
                await self.quiz_service.remove_quizzes(request.user_id, set_id)
                return jsonify({"status": "Success", "message": "Quizzes deleted successfully"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/get_sets_by_user', methods=['GET'])
        @token_required
        async def get_sets():
            try:
                sets = await self.quiz_service.list_quiz_sets(request.user_id)
                if not sets:
                    return jsonify({"error": "No quiz sets found for the user"}), 404
                return jsonify({"status": "Success", "sets": sets}), 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
        @token_required
        async def get_quiz(quiz_id):
            try:
                quiz = await self.quiz_service.fetch_quiz_details(request.user_id, quiz_id)
                if not quiz:
                    return jsonify({"error": "No quiz found for the specified ID"}), 404

                return jsonify({"status": "Success", "quiz": quiz}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        