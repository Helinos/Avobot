from database import Database

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

import time
import asyncio

database = None


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # The only Guild the bot will work with
        self.avo_cult = None

    @commands.Cog.listener()
    async def on_ready(self):
        global database
        database = await Database()

        self.avo_cult = self.bot.get_guild(556972632977965107)


    @cog_ext.cog_slash(
        name="bal",
        description="Display the amount of pits in a user's sack.",
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
                title=f"{user.name}'s Sack of Pits",
                color=discord.Color(0x00FF00),
                description=f"\n**Balance**: `₽{balance}`",
            )
            embed.set_footer(
                text="The economy functionality is still being tested,\nreport any bugs to Helinos#0001"
            )

            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)

        else:
            if member == None:
                await ctx.send(
                    "You didn't previously have a sack of pits, but you do now.\nRun the command again to see your balance."
                )
            else:
                await ctx.send(
                    "That person didn't previously have a sack of pits, but they do now.\nRun the command again to see their balance."
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
        if await database.look_for_user(user.id, "economy"):
            prev_harvest_time = await database.retrieve(
                "economy", "prev_harvest_time", user.id
            )
            since_harvest = int(time.time()) - int(prev_harvest_time)
            if since_harvest > 86400:
                balance = await database.retrieve("economy", "balance", user.id)
                if balance == None:
                    balance = 0
                new_balance = balance + 5
                await ctx.send(
                    "You harvested your Avocado tree and earned 5 pits"
                )
                await database.update("economy", "balance", new_balance, user.id)
                await database.update(
                    "economy", "prev_harvest_time", int(time.time()), user.id
                )
            else:
                th_sec = 86400 - since_harvest
                th_min = th_sec // 60
                th_hour = th_min // 60
                if th_hour == 0:
                    delta = f"{th_min} minute(s)"
                elif th_min == 0:
                    delta = f"{th_min} second(s)"
                else:
                    delta = f"{th_hour} hour(s)"
                await ctx.send(
                    f"Your Avocados aren't done growing yet! Check back in {delta}."
                )
        else:
            await ctx.send(
                "You didn't previously have a sack of pits, but you do now.\nRun the command again to harvest some Avocados."
            )

    @cog_ext.cog_slash(
        name="pay",
        description="Pay another user with pits.",
        options=[
            create_option(
                name="user",
                description="The user you want to pay.",
                option_type=6,
                required=True,
            ),
            create_option(
                name="amount",
                description="The amount you want to pay",
                option_type=4,
                required=True,
            ),
        ],
    )
    async def pay_slash(self, ctx, user: discord.User, amount: int):
        await self._pay(ctx, user, amount)

    @commands.command()
    async def pay(self, ctx, user: discord.User, amount: int):
        await ctx.trigger_typing()
        await self._pay(ctx, user, amount)

    async def _pay(self, ctx, user: discord.User, amount: int):

        payer = ctx.author
        payee = user
        if payee == payer:
            message = await ctx.send(
                "You can't pay yourself..."
            )
            await asyncio.sleep(7)
            await message.delete()
            return

        payee_exists = await database.look_for_user(payer.id, "economy")
        payer_exists = await database.look_for_user(payee.id, "economy")

        if payee_exists and payer_exists:

            payer_balance = await database.retrieve("economy", "balance", payer.id)
            payee_balance = await database.retrieve("economy", "balance", payee.id)

            if payer_balance >= amount and amount > 0:
                new_payer_balance = payer_balance - amount
                new_payee_balance = payee_balance + amount
            elif amount <= 0:
                message = await ctx.send(
                    "Nice try buddy ;)"
                )
                await asyncio.sleep(7)
                await message.delete()
                return
            else:
                message = await ctx.send(
                    "You're trying to pay more pits than you have!"
                )
                await asyncio.sleep(7)
                await message.delete()
                return

            await database.update("economy", "balance", new_payer_balance, payer.id)
            await database.update("economy", "balance", new_payee_balance, payee.id)
            await ctx.send(
                f"You have paid `₽{amount}` to {payee.mention}\nRemaining balance: `₽{new_payer_balance}`"
            )

        elif not payee_exists:
            await ctx.send(
                "You didn't previously have a sack of pits, but you do now.\nRun the command /bal to see your balance."
            )
        elif not payer_exists:
            await ctx.send(
                "The person you're trying to transfer to didn't previously have a sack of pits, but they do now.\nRun the command again to pay them with pits."
            )


    # Sends an embed with the top twenty users ordered by total balance
    @cog_ext.cog_slash(
        name="baltop",
        description="Show the server's Balance leaderboard.",
        options=[
            create_option(
                name="page",
                description="The page you want to view",
                option_type=4,
                required=False,
            )
        ],
    )
    async def baltop_slash(self, ctx, page: int = 1):
        await ctx.defer()
        await self._baltop(ctx, page)
    
    @commands.command()
    async def baltop(self, ctx, page: int = 1):
        await ctx.trigger_typing()
        await self._baltop(ctx, page)

    async def _baltop(self, ctx, page):
        page -= 1
        if page < 0:
            message = await ctx.send("Invalid page")
            await asyncio.sleep(7)
            await message.delete()
            return
        
        rows = await database.top("balance", "economy", page, ctx)

        descript = "```"

        counter = page * 20 + 1
        for combo in rows:
            user = await self.bot.fetch_user(combo[0])
            space = 40 - len(user.name) - len(str(combo[1]))
            if 100 > counter >= 10:
                space -= 1
            elif counter >= 100:
                space -= 2

            descript = (
                descript
                + "#"
                + str(counter)
                + " "
                + user.name
                + (" " * space)
                + str(combo[1])
                + "\n"
            )

            counter += 1

        descript = descript + "```"

        embed = discord.Embed(
            title=f"{self.avo_cult.name} balance leaderboard", description=descript, color=discord.Color(0x00FF00)
        )
        embed.set_footer(
            text=f"Page {page + 1} - Type /baltop {page + 2} to get page {page + 2} of the leaderboard"
        )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Economy(bot))