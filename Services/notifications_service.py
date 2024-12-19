from firebase_admin import messaging
from firebase_admin import messaging
import pytz
from threading import Thread
import uuid
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import threading
from Services.user_scheduler_manager import UserSchedulerManager

scheduler_manager = UserSchedulerManager()
scheduler = AsyncIOScheduler()

class NotificationsService:
    def __init__(self, routine_repository, jobs_repository, quiz_repository):
        self.routine_repository = routine_repository
        self.jobs_repository = jobs_repository
        self.quiz_repository = quiz_repository

    async def send_push_notification(self, token, title, body, question_id):
        try:
            notification = messaging.Notification(title=title, body=body)
            data = {"questionid": str(question_id)}
            token = token.strip()
            message = messaging.Message(notification=notification, data=data, token=token)

            print("Token:", token)
            print("Sending message:", message)

            # Running the messaging.send in an executor is needed if messaging.send is not an asyncio compatible function
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, lambda: messaging.send(message))
            
            print('Successfully sent message:', response)
        except Exception as e:
            print("Error sending message:", e)

    async def schedule_notifications(self,user_id, routine, device_token, scheduler):
        timezone = pytz.timezone('Europe/Paris')  # Example, retrieve from user settings
        for day_dict in routine['days']:
            day_of_week = day_dict['day'] - 1  # Adjusting for cron's 0-index
            for hour_dict in routine['hours']:
                time_str = hour_dict['time']
                hour, minute = map(int, time_str.split(':'))
                quiz = await self.quiz_repository.get_next_quiz_by_user(user_id)
                quiz_id = quiz['quiz_id']
                question = quiz['question']
                job_id = str(uuid.uuid4())
                job = scheduler.add_job(
                    self.send_push_notification,
                    'cron',
                    day_of_week=day_of_week,
                    hour=hour,
                    minute=minute,
                    args=[device_token, question, 'Show me what you got!', quiz_id],
                    timezone=timezone,
                    id=job_id  # Assigning the job ID
                )
                await self.jobs_repository.insert_job(job_id, user_id)
                print(f"Job {job_id} scheduled for user {user_id}")

    def run_schedule_notifications(self, user_id, routine, device_token, scheduler):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.schedule_notifications(user_id, routine, device_token, scheduler))
        finally:
            loop.close()

    async def start_routine_service(self, user_id, device_token):
        routine = await self.routine_repository.get_routine_by_user_id(user_id)
        if routine:
            # Get or create a scheduler specific to the user
            scheduler = scheduler_manager.get_scheduler(user_id)
            thread = threading.Thread(target=self.run_schedule_notifications, args=(user_id, routine, device_token, scheduler))
            thread.start()

    async def stop_routine_service(self,user_id):
        scheduler_manager.stop_scheduler(user_id)
        await self.jobs_repository.delete_job(user_id)
        
        job_ids = await self.jobs_repository.get_job_ids(user_id)
        print(f"Removing jobs {job_ids} for user {user_id}")
        for job_id in job_ids:
            lower_job_id = job_id.lower()
            scheduler.remove_job(lower_job_id)
            print(f"Job {lower_job_id} removed for user {user_id}")
        await self.jobs_repository.delete_job(user_id)

    async def update_routine_service(self, user_id):
        device_token =await self.routine_repository.get_device_token_by_userId(user_id)
        await self.stop_routine_service(user_id)
        await self.start_routine_service(user_id, device_token)