class BaseRepository:
    def __init__(self, connect):
        self.connect = connect

    async def execute_query(self, sql, params=None, fetch_one=False, commit=False, count=False, fetch_all=False):
        try:
            async with await self.connect() as conn:
                cursor = await conn.cursor()
                if isinstance(params, list) and isinstance(params[0], tuple):
                    await cursor.executemany(sql, params)
                else:
                    await cursor.execute(sql, params)
                result = None
                if fetch_one:
                    result = await cursor.fetchone()
                elif count:
                    result = (await cursor.fetchone())[0]
                elif fetch_all:
                    result = await cursor.fetchall()
                if commit:
                    await conn.commit()

                return result
        except Exception as e:
            # Log the exception or handle it as per your error policy
            print(f"Database operation failed: {e}")
            return None





    async def fetch_data(self, sql, params=None):
        async with await self.connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(sql, params)
            return await cursor.fetchall()
    
    async def execute_many(self, sql, params_list, commit=False):
        async with await self.connect() as conn:
            cursor = await conn.cursor()
            for params in params_list:
                await cursor.execute(sql, params)
            if commit:
                await conn.commit()
