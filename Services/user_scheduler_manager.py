from apscheduler.schedulers.asyncio import AsyncIOScheduler

class UserSchedulerManager:
    def __init__(self):
        self.schedulers = {}

    def get_scheduler(self, user_id):
        """Retrieve or create a new scheduler for the given user."""
        if user_id not in self.schedulers:
            self.schedulers[user_id] = AsyncIOScheduler()
            self.schedulers[user_id].start()
            print(f"Scheduler started for user {user_id}.")
        return self.schedulers[user_id]

    def stop_scheduler(self, user_id):
        """Stops and removes the scheduler for a specific user."""
        if user_id in self.schedulers and self.schedulers[user_id].running:
            self.schedulers[user_id].shutdown(wait=False)
            print(f"Scheduler stopped for user {user_id}.")
            del self.schedulers[user_id]

    def stop_all_schedulers(self):
        """Stops all schedulers and clears the scheduler dictionary."""
        for user_id, scheduler in self.schedulers.items():
            if scheduler.running:
                scheduler.shutdown(wait=False)
                print(f"Scheduler stopped for user {user_id}.")
        self.schedulers.clear()
        print("All schedulers stopped.")