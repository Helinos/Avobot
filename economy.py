from main import sql_update, sql_retrieve

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

import aiosqlite
import time


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def look_for_user_in_db(self, user_id):
        db = await aiosqlite.connect("main.db")
        cursor = await db.execute(
            f"SELECT EXISTS(SELECT 1 FROM economy WHERE user_id = {user_id})"
        )
        tupled = await cursor.fetchone()
        if tupled[0] == 0:
            # user_id balance prev_harvest_time
            await db.execute(
                f"INSERT INTO economy VALUES ({user_id}, 0, 0)"
            )
            await db.commit()
            await cursor.close()
            await db.close()
            return False
        else:
            await cursor.close()
            await db.close()
            return True


    @cog_ext.cog_slash(
        name="bal",
        description="Display the amount of pits in a user's stash.",
        options=[
            create_option(
                name="user",
                description="The user who you want the information of.",
                option_type=6,
                required=False,
            )
        ],
    )
    async def bal_slash(self, ctx, member: discord.Member = None):
        await self._bal(ctx, member)

    @commands.command()
    async def bal(self, ctx, member: discord.Member = None):
        await ctx.trigger_typing()
        await self._bal(ctx, member)

    async def _bal(self, ctx, member):
        if member == None:
            user = ctx.author
        else:
            user = member

        if user == None:
            return

        if await self.look_for_user_in_db(user.id):
            balance = await sql_retrieve("economy", "balance", user.id)
            
            if balance == None:
                balance = 0
            
            embed = discord.Embed(
                title=f"{user.name}'s Pit Stash", color=discord.Color(0x00FF00),
                description=f"\n**Balance**: `₧ {balance}`",
            )
            embed.set_footer(
                text="The economy functionality is still being tested,\nreport any bugs to Helinos#0001"
            )

            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)

        else:
            if member == None:
                await ctx.send(
                    "You didn't previously have a stash of pits, but you do now.\nRun the command again to see your balance."
                )
            else:
                await ctx.send(
                    "That person didn't previously have a stash of pits, but they do now.\nRun the command again to see their balance."
                )

    @cog_ext.cog_slash(
        name="harvest",
        description="Pick fresh Avocados and harvest their pits.",
    )
    async def harvest_slash(self, ctx):
        await self._harvest(ctx)

    @commands.command()
    async def harvest(self, ctx):
        await ctx.trigger_typing()
        await self._harvest(ctx)

    async def _harvest(self, ctx):
        user = ctx.author
        prev_harvest_time = await sql_retrieve("economy", "prev_harvest_time", user.id)
        since_harvest = (int(time.time()) - int(prev_harvest_time))
        if since_harvest > 86400:
            balance = await sql_retrieve("economy", "balance", user.id)
            if balance == None:
                balance = 0
            new_balance = balance + 5
            await ctx.send("You harvested your Avocado tree and were able to earn 5 pits")
            await sql_update("economy", "balance", new_balance, user.id)
            await sql_update("economy", "prev_harvest_time", int(time.time()), user.id)
        else:
            await ctx.send(f"You Avocados aren't done growing yet! Check back in {86400 - since_harvest} seconds.")

def setup(bot):
    bot.add_cog(Economy(bot))