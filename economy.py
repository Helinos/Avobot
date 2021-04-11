from database import Database

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

import time

database = None

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global database
        database = await Database()

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

        if await database.look_for_user(user.id, "economy"):
            balance = await database.retrieve("economy", "balance", user.id)
            
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
        prev_harvest_time = await database.retrieve("economy", "prev_harvest_time", user.id)
        since_harvest = (int(time.time()) - int(prev_harvest_time))
        if since_harvest > 86400:
            balance = await database.retrieve("economy", "balance", user.id)
            if balance == None:
                balance = 0
            new_balance = balance + 5
            await ctx.send("You harvested your Avocado tree and were able to earn 5 pits")
            await database.update("economy", "balance", new_balance, user.id)
            await database.update("economy", "prev_harvest_time", int(time.time()), user.id)
        else:
            th_sec = 86400 - since_harvest
            th_min = th_sec // 60
            th_hour = th_min // 60
            if th_hour == 0:
                delta = f"{th_min} minutes"
            elif th_min == 0:
                delta = f"{th_min} seconds"
            else:
                delta = f"{th_hour} hours"
            await ctx.send(f"You Avocados aren't done growing yet! Check back in {delta}.")

def setup(bot):
    bot.add_cog(Economy(bot))