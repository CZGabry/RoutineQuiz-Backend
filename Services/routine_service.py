# routine_service.py
class RoutineService:
    def __init__(self, routine_repository, notifications_service):
        self.routine_repository = routine_repository
        self.notifications_service = notifications_service

    async def manage_routine(self, user_id, selected_days, hours):
        existing_routine = await self.routine_repository.get_routine_by_user_id(user_id)
        existing_days = {day['day'] for day in existing_routine['days']}
        existing_hours = {hour['time'] for hour in existing_routine['hours']}

        days_to_insert = set(selected_days) - existing_days
        days_to_delete = existing_days - set(selected_days)
        hours_to_insert = {hour['time'] for hour in hours if hour['time'] not in existing_hours}
        hours_to_delete = existing_hours - {hour['time'] for hour in hours}

        await self.routine_repository.insert_routine_days(user_id, days_to_insert)
        await self.routine_repository.delete_routine_days(user_id, days_to_delete)
        await self.routine_repository.insert_routine_hours(user_id, hours_to_insert)
        await self.routine_repository.delete_routine_hours(user_id, hours_to_delete)
        await self.notifications_service.update_routine_service(user_id)

    async def get_routine(self, user_id):
        return await self.routine_repository.get_routine_by_user_id(user_id)
