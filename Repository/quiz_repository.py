
from .Base.base_repository import BaseRepository
class QuizRepository(BaseRepository):
    def __init__(self, get_connection):
        super().__init__(get_connection)

    async def insert_quiz(self, quiz_objects, user_id, topic):
        insert_set_query = """
            INSERT INTO QUIZDB.dbo.QuizSet (Topic, NumberOfQuestions, UserID)
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?);
        """
        set_data = (topic, len(quiz_objects), user_id)
        quiz_set_id = await self.execute_query(insert_set_query, set_data, fetch_one=True, commit=True)

        if not quiz_set_id:
            return

        quiz_objects_data = []
        for quiz in quiz_objects:
            options = quiz['options'] + [None] * (4 - len(quiz['options']))  # Ensure there are always four options
            data = (quiz['question'], *options, chr(65 + quiz['correct_answer_index']), 1, user_id, quiz['explanation'], quiz_set_id[0])
            quiz_objects_data.append(data)

        # Insert quiz objects
        insert_quiz_query = """
            INSERT INTO QUIZDB.dbo.Quiz (Question, OptionA, OptionB, OptionC, OptionD, CorrectAnswer, CategoryID, UserId, Explanation, QuizSetId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        await self.execute_many(insert_quiz_query, quiz_objects_data, commit=True)

    async def _get_last_inserted_id(self):
        """Retrieves the last inserted ID from the database."""
        query = "SELECT SCOPE_IDENTITY();"
        result = await self.execute_query(query, fetch_one=True)
        return result[0] if result else None

    async def _insert_quiz_objects(self, cursor, quiz_objects, user_id, quiz_set_id):
        insert_quiz_query = """
        INSERT INTO QUIZDB.dbo.Quiz (Question, OptionA, OptionB, OptionC, OptionD, CorrectAnswer, CategoryID, UserId, Explanation, QuizSetId)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        for quiz in quiz_objects:
            options = quiz['options'] + [None] * (4 - len(quiz['options']))  # Ensure there are always four options
            data = (quiz['question'], *options, chr(65 + quiz['correct_answer_index']), 1, user_id, quiz['explanation'], quiz_set_id)
            await self.execute_query(insert_quiz_query, data, commit=True)

    async def get_quizzes_by_user(self, user_id, set_id):
        select_query = """
            SELECT QuizID, Question, OptionA, OptionB, OptionC, OptionD, CorrectAnswer
            FROM QUIZDB.dbo.Quiz
            WHERE UserID = ? AND QuizSetId = ?;
        """
        rows = await self.execute_query(select_query, (user_id, set_id), fetch_all=True)
        
        # Convert rows to dictionaries
        quizzes = []
        for row in rows:
            quiz = {
                'quiz_id': row[0],
                'question': row[1],
                'options': [row[2], row[3], row[4], row[5]],
                'correct_answer': row[6]
            }
            quizzes.append(quiz)
            
        return quizzes

    async def delete_quizzes_by_user_and_set(self, user_id, set_id):
        delete_quiz_query = """
            DELETE FROM QUIZDB.dbo.Quiz
            WHERE UserID = ? AND QuizSetId = ?;
        """
        delete_set_query = """
            DELETE FROM QUIZDB.dbo.QuizSet
            WHERE UserID = ? AND Id = ?;
        """
        await self.execute_query(delete_quiz_query, (user_id, set_id), commit=True)
        await self.execute_query(delete_set_query, (user_id, set_id), commit=True)

    async def check_quizzes_exist_for_user(self, user_id):
        count_query = """
            SELECT COUNT(*)
            FROM QUIZDB.dbo.Quiz
            WHERE UserID = ?;
        """
        result = await self.execute_query(count_query, (user_id,), fetch_one=True)
        return result[0] > 0

    async def get_quiz_by_id(self, user_id, quiz_id):
        select_query = """
            SELECT QuizID, Question, OptionA, OptionB, OptionC, OptionD, CorrectAnswer, Explanation
            FROM QUIZDB.dbo.Quiz
            WHERE UserID = ? AND QuizID = ?;
        """
        row = await self.execute_query(select_query, (user_id, quiz_id), fetch_one=True)

        if row:
            quiz = {
                'quiz_id': row[0],
                'question': row[1],
                'options': [row[2], row[3], row[4], row[5]],
                'correct_answer': row[6],
                'explanation': row[7]
            }
            return quiz
        else:
            return None

    async def get_next_quiz_by_user(self, user_id):
        """Retrieves the next quiz for a specific user."""
        check_query = """
            SELECT COUNT(*)
            FROM QUIZDB.dbo.Quiz
            WHERE (Sent IS NULL OR Sent = 0) AND UserID = ?;
        """
        count = await self.execute_query(check_query, (user_id,), fetch_one=True, count=True)  # Set count=True to retrieve the count value
        if count[0] == 0:
            reset_query = """
                UPDATE QUIZDB.dbo.Quiz
                SET Sent = 0
                WHERE UserID = ?;
            """
            await self.execute_query(reset_query, (user_id,), commit=True)

        select_query = """
            SELECT TOP 1 QuizID, Question, OptionA, OptionB, OptionC, OptionD, CorrectAnswer, Sent, Explanation
            FROM QUIZDB.dbo.Quiz
            WHERE (Sent IS NULL OR Sent = 0) AND UserID = ?
            ORDER BY QuizID;
        """
        row = await self.execute_query(select_query, (user_id,), fetch_one=True)
        
        if row:  # Check if row is not None
            update_query = """
                UPDATE QUIZDB.dbo.Quiz
                SET Sent = 1
                WHERE QuizID = ? AND UserID = ?;
            """
            await self.execute_query(update_query, (row[0], user_id), commit=True)
            
            return {
                'quiz_id': row[0],
                'question': row[1],
                'options': [row[2], row[3], row[4], row[5]],
                'correct_answer': row[6],
                'explanation': row[8]
            }
        return None



    async def get_sets_by_user(self, user_id):
        select_query = """
            SELECT Id, Topic, NumberOfQuestions
            FROM QUIZDB.dbo.QuizSet
            WHERE UserID = ?;
        """
        rows = await self.execute_query(select_query, (user_id,), fetch_all=True)
        return [{'set_id': row[0], 'topic': row[1], 'number_of_questions': row[2]} for row in rows]
