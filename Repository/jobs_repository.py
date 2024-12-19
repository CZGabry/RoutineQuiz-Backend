from .Base.base_repository import BaseRepository

class JobsRepository(BaseRepository):
    def __init__(self, db_connection):
        super().__init__(db_connection)

    async def insert_job(self, job_id, user_id):
        """Inserts a job into the database."""
        query = "INSERT INTO QUIZDB.dbo.ScheduledJobs (JobID, UserID) VALUES (?, ?)"
        await self.execute_query(query, (job_id, user_id), commit=True)

    async def get_job_ids(self, user_id):
        """Retrieves all job IDs for a specific user."""
        query = "SELECT JobID FROM QUIZDB.dbo.ScheduledJobs WHERE UserID = ?"
        rows = await self.fetch_data(query, (user_id,))
        return [row[0] for row in rows]

    async def delete_job(self, user_id):
        """Deletes all jobs for a specific user."""
        query = "DELETE FROM QUIZDB.dbo.ScheduledJobs WHERE UserID = ?"
        await self.execute_query(query, (user_id,), commit=True)