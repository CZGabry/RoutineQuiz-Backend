import openai

# Set your OpenAI API key here

async def generate_quiz(sentence, number_of_questions):
    print("Input sentence:", sentence)
    formatted_content = content_formatter(sentence, number_of_questions)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": formatted_content}
            ],
        )
        quiz_question = response['choices'][0]['message']['content']
        print("Quiz:", quiz_question)
        return quiz_question
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def get_quiz_objects(sentence, number_of_questions):
    return await generate_quiz(sentence, number_of_questions)

def content_formatter(sentence, number_of_questions):
    # Use triple quotes for multi-line string to avoid confusion with inner quotes
    example_structure = """
        {
            "topic": "Detected topic of the sentence",
            "quiz": [
                {
                    "question": "Your question here",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer_index": 0,  # 0-based index for the correct option
                    "explanation": "Explanation for why this is the correct answer",
                    "difficulty": "medium"  # Difficulty level of the question
                }
                # More quiz objects can be added following the same structure
            ]
        }"""
    prompt = (
        'Generate a json object containing a quiz in Python list format preceded by the detected topic, topic must be one for entire json. Each quiz object should contain a question, '
        'four options labeled from A to D, and the index (0-based) of the correct answer. '
        'Ensure the questions are informative, the options plausible, and the structure consistent with the example provided. '
        'Keep the focus on clarity and educational value, aiming for a variety of difficulty levels across the questions. '
        'Inside question and options string values, only use the following characters: a-z, A-Z, 0-9, and punctuation. No double quotes or backticks. '
        'Based on the arguments detected, generate {} questions. The array values should be ready to be converted into a list. '
        'Generate a quick explanation of the correct answer for each question. '
        'Very important: your response must be just the JSON object and have to necessarly start with a curly bracket. '
        'Here is an example of how each quiz object should be structured: {}'.format(number_of_questions, example_structure)
    )
    content = "Based on the following sentence or note: '{}' {}\n\nEnsure the generated code is syntactically correct and ready for use.".format(sentence, prompt)
    return content
