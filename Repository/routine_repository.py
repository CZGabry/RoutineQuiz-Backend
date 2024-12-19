
from .Base.base_repository import BaseRepository
class RoutineRepository(BaseRepository):
    def __init__(self, connect):
        super().__init__(connect)

    async def insert_routine_days(self, user_id, days_to_insert):
        if days_to_insert:
            await self.execute_query(
                "INSERT INTO QUIZDB.dbo.UserRoutineDays (UserID, DayOfWeek) VALUES (?, ?)",
                [(user_id, day) for day in days_to_insert],
                commit=True
            )

    async def delete_routine_days(self, user_id, days_to_delete):
        if days_to_delete:
            await self.execute_query(
                "DELETE FROM QUIZDB.dbo.UserRoutineDays WHERE UserID = ? AND DayOfWeek = ?",
                [(user_id, day) for day in days_to_delete],
                commit=True
            )

    async def insert_routine_hours(self, user_id, hours_to_insert):
        if hours_to_insert:
            await self.execute_query(
                "INSERT INTO QUIZDB.dbo.UserRoutineHours (UserID, NotificationTime) VALUES (?, ?)",
                [(user_id, hour) for hour in hours_to_insert],
                commit=True
            )

    async def delete_routine_hours(self, user_id, hours_to_delete):
        if hours_to_delete:
            await self.execute_query(
                "DELETE FROM QUIZDB.dbo.UserRoutineHours WHERE UserID = ? AND NotificationTime = ?",
                [(user_id, hour) for hour in hours_to_delete],
                commit=True
            )

    async def get_routine_by_user_id(self, user_id):
        days = await self.fetch_data("SELECT DayOfWeek FROM QUIZDB.dbo.UserRoutineDays WHERE UserID = ?", user_id)
        hours = await self.fetch_data("SELECT NotificationTime FROM QUIZDB.dbo.UserRoutineHours WHERE UserID = ?", user_id)
        return {
            'days': [{'day': day[0]} for day in days],
            'hours': [{'time': hour[0].strftime('%H:%M')} for hour in hours]
        }

    async def get_device_token_by_userId(self, user_id):
        """Fetches the device token for a specific user."""
        query = "SELECT DeviceToken FROM QUIZDB.dbo.Users WHERE UserID = ?"
        result = await self.fetch_data(query, (user_id,))
        return result[0][0] if result else None
