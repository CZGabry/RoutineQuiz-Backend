# app.py
from quart import Quart, request
from quart_cors import cors
from Controllers.quiz_controller import QuizController  # Ensure this controller is async compatible
from Controllers.users_controller import UserController  # Ensure this controller is async compatible
from config.firebase import initialize_firebase
from Controllers.routine_controller import RoutineController  # Ensure this controller is async compatible
from functools import partial
import json
import asyncodbc
from Controllers.auth_token.middleware import token_required

from Repository.Base.base_repository import BaseRepository
from Repository.users_repository import UserRepository
from Repository.routine_repository import RoutineRepository
from Repository.quiz_repository import QuizRepository
from Repository.jobs_repository import JobsRepository

from Services.user_service import UserService
from Services.routine_service import RoutineService
from Services.quiz_service import QuizService
from Services.notifications_service import NotificationsService

app = Quart(__name__)
cors(app)  # Apply CORS using quart-cors

async def setup_app():
    initialize_firebase()
    print("Starting routine service...")

@app.before_serving
async def startup():
    await setup_app()

async def before_request():
    if request.path.startswith('/api'):
        return None

app.before_request(before_request)

def load_db_config(config_path='db_config.json'):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config['conn_str']

async def connection_factory():
    conn_str = load_db_config()
    return await asyncodbc.connect(dsn=conn_str)

if __name__ == '__main__':

    # TODO Container for services and repos init
    
    user_repository = UserRepository(connection_factory)
    user_service = UserService(user_repository)
    user_controller = UserController(app, user_service)

    
    

    quiz_repository = QuizRepository(connection_factory)
    quiz_service = QuizService(quiz_repository)
    quiz_controller = QuizController(app, quiz_service)

    jobs_repository = JobsRepository(connection_factory)

    routine_repository = RoutineRepository(connection_factory)
    notifications_service = NotificationsService(routine_repository, jobs_repository, quiz_repository)
    routine_service = RoutineService(routine_repository, notifications_service)
    routine_controller = RoutineController(app, routine_service)

    app.run(debug=True, host='0.0.0.0', port=5050, use_reloader=False)
