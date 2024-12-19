import json

def format_quiz_array(input_string):
    data = json.loads(input_string)
    topic = data['topic']
    python_list = data['quiz']
    return python_list, topic

