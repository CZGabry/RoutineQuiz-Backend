from open_ai_quiz import get_quiz_objects
from response_formatter import format_quiz_array
class QuizService:
    def __init__(self, quiz_repository):
        self.quiz_repository = quiz_repository

    async def handle_quiz_creation(self, user_id, sentence, number_of_questions):
        quiz_array_string = await get_quiz_objects(sentence, number_of_questions)
        quiz_array, topic = format_quiz_array(quiz_array_string)  # Ensure this is refactored appropriately
        await self.quiz_repository.insert_quiz(quiz_array, user_id, topic)
        return quiz_array, topic

    async def fetch_quizzes(self, user_id, set_id):
        return await self.quiz_repository.get_quizzes_by_user(user_id, set_id)

    async def fetch_quiz_details(self, user_id, quiz_id):
        return await self.quiz_repository.get_quiz_by_id(user_id, quiz_id)

    async def remove_quizzes(self, user_id, set_id):
        await self.quiz_repository.delete_quizzes_by_user_and_set(user_id, set_id)

    async def list_quiz_sets(self, user_id):
        return await self.quiz_repository.get_sets_by_user(user_id)

    async def fetch_next_quiz(self):
        return await self.quiz_repository.get_next_quiz()

    async def check_quizzes_exist(self, user_id):
        return await self.quiz_repository.check_quizzes_exist_for_user(user_id)
