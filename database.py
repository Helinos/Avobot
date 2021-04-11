import asyncio
import aiosqlite
from asyncinit import asyncinit

@asyncinit
class Database():
    async def __init__(self):
        self.db = await aiosqlite.connect("main.db")
    
    # async def raw(self, command: str):
    #    await self.db.execute(command)


    # Retrieve a value from the database
    async def retrieve(self, table: str, coloumn: str, user_id: int):
        cursor = await self.db.execute(
            f"SELECT {coloumn} FROM {table} WHERE user_id = {user_id}"
        )
        try:
            tupled = await cursor.fetchone()
            value = tupled[0]
            await cursor.close()
            return value
        except TypeError:
            print(f"Getting the value of {coloumn} from {user_id} returned a NoneType.")
            await cursor.close()
            return None

    # Update a value in the database
    async def update(self, table: str, coloumn: str, value: int, user_id: int):
        await self.db.execute(
            f"UPDATE {table} SET {coloumn} = {value} WHERE user_id = {user_id}"
        )
        await self.db.commit()


    # Returns false if the user didn't previously have an entry and makes an extry for them, returns true if they did
    async def look_for_user(self, user_id, table):
        cursor = await self.db.execute(
            f"SELECT EXISTS(SELECT 1 FROM {table} WHERE user_id = {user_id})"
        )
        tupled = await cursor.fetchone()
        if tupled[0] == 0:  
            # user_id text voice prev_message_time text_level voice_level total_exp total_level
            if table == "exp":
                await self.db.execute(
                    f"INSERT INTO {table} VALUES ({user_id}, 0, 0, 0, 0, 0, 0, 0)"
                )
            elif table == "economy":
                await self.db.execute(
                    f"INSERT INTO economy VALUES ({user_id}, 0, 0)"
                )
            await self.db.commit()
            await cursor.close()
            return False
        else:
            await cursor.close()
            return True


    # Get a leaderboard from a table
    async def top(self, column: str, table: str, page: int, ctx):
        # Connect to the database and select every row
        cursor = await self.db.execute("SELECT Count(*) FROM exp")

        # Get the maximum amound of entries
        max = await cursor.fetchone()
        max = max[0]
        
        lower_limit = page * 20
        upper_limit = lower_limit + 20
        if upper_limit > max:
            upper_limit = max
        if lower_limit > max:
            # Wondering if I should replace this with a raise to avoid sending ctx
            await ctx.send("Invalid page.")
            return

        cursor = await self.db.execute(
            f"SELECT user_id,{column} FROM {table} ORDER BY total_exp DESC LIMIT {lower_limit},{20}"
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return rows
