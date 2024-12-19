from .Base.base_repository import BaseRepository
class UserRepository(BaseRepository):
    def __init__(self, get_connection):
        super().__init__(get_connection)

    async def find_user_by_credentials(self, identifier, hashed_password):
        query = """SELECT UserID, DeviceToken FROM Users WHERE (Username = ? OR Email = ?) AND PasswordHash = ?;"""
        return await self.execute_query(query, (identifier, identifier, hashed_password), fetch_one=True)

    async def update_device_token(self, user_id, device_token):
        query = """UPDATE Users SET DeviceToken = ? WHERE UserID = ?;"""
        await self.execute_query(query, (device_token, user_id), commit=True)

    async def add_user(self, username, hashed_password, email):
        query = """INSERT INTO Users (Username, PasswordHash, Email) VALUES (?, ?, ?);"""
        await self.execute_query(query, (username, hashed_password, email), commit=True)

    async def check_user_exists(self, username, email):
        query = """SELECT COUNT(1) FROM Users WHERE Username = ? OR Email = ?;"""
        result = await self.execute_query(query, (username, email), fetch_one=True)
        return result[0] > 0

    async def get_username_by_id(self, user_id):
        query = """SELECT Username FROM Users WHERE UserID = ?;"""
        result = await self.execute_query(query, (user_id,), fetch_one=True)
        return result[0]
