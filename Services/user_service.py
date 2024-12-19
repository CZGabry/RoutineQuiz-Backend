from Repository.users_repository import UserRepository
from hashlib import sha256

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    async def register_user(self, username, password, email):
        if await self.user_repository.check_user_exists(username, email):
            return False, "Username or Email already exists"
        hashed_password = self.hash_password(password)
        await self.user_repository.add_user(username, hashed_password, email)
        return True, "User registered successfully"

    async def login_user(self, identifier, password, device_token):
        hashed_password = self.hash_password(password)
        result = await self.user_repository.find_user_by_credentials(identifier, hashed_password)
        if result:
            user_id, current_device_token = result
            if current_device_token != device_token:
                await self.user_repository.update_device_token(user_id, device_token)
            return True, user_id
        return False, None

    def hash_password(self, password):
        return sha256(password.encode('utf-8')).hexdigest()