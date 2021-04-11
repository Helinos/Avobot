from database import Database

import discord
from discord.ext import commands
from discord.ext.tasks import loop
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

import random
import asyncio
import math
import time
from asyncinit import asyncinit

database = None

class Leveler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.vc_monitor.start()

        # The only Guild the bot will work with
        self.avo_cult = None

        # Hardcoded Text Channels
        self.level_spam = None
        self.level_spam_id = 815706720139345941

        # Hardcoded Voice Channels
        self.xbox_live = None
        self.xbox_live_id = 772648971758862346
        self.mobile_phone = None
        self.mobile_phone_id = 734290456979963975
        self.chilling = None
        self.chilling_id = 779488830893195325
        self.freezing = None
        self.freezing_id = 826191838901567538
        self.lvl_5 = None
        self.lvl_5_id = 684585066692739112
        self.booster = None
        self.booster_id = 826191768797184030

        # Voice Channels list filled in on_ready()
        self.voice_channels = None

        # Hardcoded Level Roles
        self.level_roles: dict = {
            1: 815488480687816715,
            3: 815488894832476190,
            5: 815488924876931094,
            10: 815489054824333382,
            15: 815489062005112843,
            20: 815489073266819112,
            25: 815489067345117206,
            30: 815489379463987224,
            35: 815489374145478658,
            40: 815489384374861854,
            45: 815489393162453022,
            50: 815489388749258762,
            55: 815489682506121236,
            60: 815489690673086474,
            65: 815489696112705536,
            70: 815490016587022336,
        }

    # Main VC monitor, check every voice chat once a minute and award EXP to user in a voice chat that was atleast 2 other users in it.
    @loop(seconds=120)
    async def vc_monitor(self):
        # Get the users in every voice channel
        for i in self.voice_channels:
            occupant_ids = list(i.voice_states.keys())
            occupant_states = list(i.voice_states.values())
            eligible_ids = []
            counter = 0

            # Trim ineligible users
            for user_id in occupant_ids:
                user = await self.bot.fetch_user(user_id)
                # Trim bots from the list of user ids
                if (
                    not user.bot
                    and not occupant_states[counter].deaf
                    and not occupant_states[counter].mute
                    and not occupant_states[counter].self_deaf
                    and not occupant_states[counter].self_mute
                ):
                    eligible_ids.append(user_id)
                counter += 1

            # Award EXP to each user
            if len(eligible_ids) >= 3:
                for user_id in eligible_ids:
                    if await database.look_for_user(user.id, "exp"):

                        user = await self.bot.fetch_user(user_id)

                        # Award EXP
                        prev_exp = await database.retrieve("exp", "voice", user_id)
                        new_exp = prev_exp + random.randint(10, 20)
                        await database.update("exp", "voice", new_exp, user_id)

                        # Adjust level if need to
                        prev_level = 0
                        prev_level = await database.retrieve("exp", "voice_level", user_id)
                        if prev_level == None:
                            prev_level = 0
                        calculated_level = await self.level_from_exp(new_exp)
                        if calculated_level != prev_level:
                            await database.update(
                                "exp", "voice_level", calculated_level, user_id
                            )
                            await self.level_spam.send(
                                f"{user.mention} reached **Voice Level {calculated_level}**!"
                            )

                        await self.check_levelroles(user)

    # Wait for the bot to be ready before starting the vc monitor loop
    @vc_monitor.before_loop
    async def vc_monitor_before(self):
        await self.bot.wait_until_ready()


    # Returns false if the user didn't previously have an entry and makes an extry for them, returns true if they did
    # async def look_for_user_in_db(self, user_id):
    #     db = await aiosqlite.connect("main.db")
    #     cursor = await db.execute(
    #         f"SELECT EXISTS(SELECT 1 FROM exp WHERE user_id = {user_id})"
    #     )
    #     tupled = await cursor.fetchone()
    #     if tupled[0] == 0:  
    #         # user_id text voice prev_message_time text_level voice_level total_exp total_level
    #         await db.execute(
    #             f"INSERT INTO exp VALUES ({user_id}, 0, 0, 0, 0, 0, 0, 0)"
    #         )
    #         await db.commit()
    #         await cursor.close()
    #         await db.close()
    #         return False
    #     else:
    #         await cursor.close()
    #         await db.close()
    #         return True


    # Basic equations for caluclating level
    async def level_from_exp(self, exp):
        return math.floor(math.sqrt(9 * (exp) / 625))

    def exp_from_level(self, level: int):
        return math.floor((625 * (level ** 2)) / 9)

    # Check what roles the user has, what roles the user should have, and give the user any missing roles
    async def check_levelroles(self, user):

        text_exp = await database.retrieve("exp", "text", user.id)
        voice_exp = await database.retrieve("exp", "voice", user.id)

        total_exp = text_exp + voice_exp
        total_level = await self.level_from_exp(total_exp)
        await database.update("exp", "total_exp", total_exp, user.id)
        await database.update("exp", "total_level", total_level, user.id)

        member = await self.avo_cult.fetch_member(user.id)

        should_haves = []

        for req_level in list(self.level_roles.keys()):
            if total_level >= req_level:
                should_haves.append(self.level_roles[req_level])
            else:
                break

        for sh_role_id in should_haves:
            if not sh_role_id in [role.id for role in member.roles]:
                needed_role = self.avo_cult.get_role(sh_role_id)
                try:
                    await member.add_roles(needed_role, reason="Leveled Up")
                    await self.level_spam.send(
                        f"{user.mention} has just reached **Total {needed_role.name}** and was rewarded with a role!"
                    )
                except discord.HTTPException:
                    print("Assigning roles rate limited")


    @commands.Cog.listener()
    async def on_ready(self):
        self.avo_cult = self.bot.get_guild(556972632977965107)

        self.xbox_live = self.bot.get_channel(self.xbox_live_id)
        self.mobile_phone = self.bot.get_channel(self.mobile_phone_id)
        self.chilling = self.bot.get_channel(self.chilling_id)
        self.freezing = self.bot.get_channel(self.freezing_id)
        self.lvl_5 = self.bot.get_channel(self.lvl_5_id)
        self.booster = self.bot.get_channel(self.booster_id)

        self.voice_channels = [
            self.xbox_live,
            self.mobile_phone,
            self.chilling,
            self.freezing,
            self.lvl_5,
            self.booster,
        ]

        self.level_spam = self.bot.get_channel(self.level_spam_id)
        
        global database
        database = await Database()


    # Award EXP for sending a message every minute and make sure commands are only done in #other-bots
    @commands.Cog.listener()
    async def on_message(self, ctx):
        user = ctx.author
        if await database.look_for_user(user.id, "exp") and not user.bot:
            # On message send get the time of the last message
            prev_message_time = await database.retrieve("exp", "prev_message_time", user.id)
            if prev_message_time == None:
                prev_message_time = 0
            # See if it's been a minute since the last message
            if (int(time.time()) - int(prev_message_time)) > 120:

                # Award EXP
                prev_exp = await database.retrieve("exp", "text", user.id)
                new_exp = prev_exp + random.randint(10, 20)
                await database.update("exp", "text", new_exp, user.id)
                await database.update("exp", "prev_message_time", int(time.time()), user.id)

                # Adjust level if need to
                prev_level = await database.retrieve("exp", "text_level", user.id)
                if prev_level == None:
                    prev_level = 0
                calculated_level = await self.level_from_exp(new_exp)
                if calculated_level != prev_level:
                    await database.update("exp", "text_level", calculated_level, user.id)
                    await self.level_spam.send(
                        f"{ctx.author.mention} reached **Text Level {calculated_level}**!"
                    )

                await self.check_levelroles(user)

    @cog_ext.cog_slash(
        name="level",
        description="Display a user's current levels and progress.",
        options=[
            create_option(
                name="user",
                description="The user who you want the information of.",
                option_type=6,
                required=False,
            )
        ],
    )
    async def level_slash(self, ctx, member: discord.Member = None):
        await self._level(ctx, member)

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        await ctx.trigger_typing()
        await self._level(ctx, member)

    async def _level(self, ctx, member):
        if member == None:
            user = ctx.author
        else:
            user = member

        if user == None:
            return

        if await database.look_for_user(user.id, "exp"):
            text_level = await database.retrieve("exp", "text_level", user.id)
            voice_level = await database.retrieve("exp", "voice_level", user.id)
            text_exp = await database.retrieve("exp", "text", user.id)
            voice_exp = await database.retrieve("exp", "voice", user.id)

            if text_level == None:
                text_level = 0
            if voice_level == None:
                voice_level = 0

            total_exp = text_exp + voice_exp
            total_level = await self.level_from_exp(total_exp)

            embed = discord.Embed(
                title=f"{user.name}'s level card", color=discord.Color(0xFF00FF)
            )
            embed.add_field(
                name="Text:",
                value=f"```[Level: {text_level}][{await self.make_level_bar(text_level, text_exp)}][Level: {text_level + 1}]\nTotal to next level: [{text_exp}/{self.exp_from_level(text_level + 1)}]```",
                inline=False,
            )
            embed.add_field(
                name="Voice:",
                value=f"```[Level: {voice_level}][{await self.make_level_bar(voice_level, voice_exp)}][Level: {voice_level + 1}]\nTotal to next level: [{voice_exp}/{self.exp_from_level(voice_level + 1)}]```",
                inline=False,
            )
            embed.add_field(
                name="Total:",
                value=f"```[Level: {total_level}][{await self.make_level_bar(total_level, total_exp)}][Level: {total_level + 1}]\nTotal to next level: [{total_exp}/{self.exp_from_level(total_level + 1)}]```",
                inline=False,
            )
            embed.set_footer(
                text="DM @Helinos#0001 if you'd like your old (tatsumaki) score transfered to this bot."
            )

            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)

        else:
            if member == None:
                await ctx.send(
                    "You weren't registered in the database previously, but you are now.\nRun the command again to see your level."
                )
            else:
                await ctx.send(
                    "That person wasn't registered in the database previously, but they are now.\nRun the command again to see their level."
                )

    async def make_level_bar(self, level: int, current_exp: int):
        this_level_exp = self.exp_from_level(level)
        next_level_exp = self.exp_from_level(level + 1)

        exp_range = next_level_exp - this_level_exp
        progress_exp = current_exp - this_level_exp
        max_characters = 30
        filled_characters = math.floor(max_characters * (progress_exp / exp_range))

        exp_bar = ""
        for i in range(max_characters):
            if filled_characters > 0:
                exp_bar = exp_bar + "="
                filled_characters -= 1
            else:
                exp_bar = exp_bar + "-"
        return exp_bar

    # Sends an embed with the users current scores
    @cog_ext.cog_slash(
        name="exp",
        description="Display a user's EXP.",
        options=[
            create_option(
                name="user",
                description="The user who you want the information of.",
                option_type=6,
                required=False,
            )
        ],
    )
    async def exp_slash(self, ctx, member: discord.Member = None):
        await self._exp(ctx, member)

    @commands.command()
    async def exp(self, ctx, member: discord.Member = None):
        await ctx.trigger_typing()
        await self._exp(ctx, member)

    async def _exp(self, ctx, member):
        if member == None:
            user = ctx.author
        else:
            user = member
        if user == None:
            ctx.send("Invalid user.")

        if await database.look_for_user(user.id, "exp"):
            text_exp = await database.retrieve("exp", "text", user.id)
            voice_exp = await database.retrieve("exp", "voice", user.id)

            total = "{:,}".format(text_exp + voice_exp)
            text_exp = "{:,}".format(text_exp)
            voice_exp = "{:,}".format(voice_exp)

            embed = discord.Embed(
                title=f"{user.name}'s EXP card",
                description=f"**Text**: `{text_exp}`\n**Voice**: `{voice_exp}`\n**Total**: `{total}`",
                color=discord.Color(0xFF00FF),
            )
            embed.set_footer(
                text="DM @Helinos#0001 if you'd like your\ntatsumaki score transfered to this bot."
            )
            embed.set_thumbnail(url=user.avatar_url)

            await ctx.send(embed=embed)

        else:
            if member == None:
                await ctx.send(
                    "You weren't registered in the database previously, but you are now.\nRun the command again to see your exp."
                )
            else:
                await ctx.send(
                    "That person wasn't registered in the database previously, but they are now.\nRun the command again to see their exp."
                )

    # Sends an embed with the top ten users ordered by total exp
    @cog_ext.cog_slash(
        name="top",
        description="Display a user's EXP.",
        options=[
            create_option(
                name="page",
                description="Show the server leaderboard.",
                option_type=4,
                required=False,
            )
        ],
    )
    async def top_slash(self, ctx, page: int = 1):
        await ctx.defer()
        await self._top(ctx, page)
    
    @commands.command()
    async def top(self, ctx, page: int = 1):
        await ctx.trigger_typing()
        await self._top(ctx, page)

    async def _top(self, ctx, page):
        page -= 1
        if page < 0:
            message = await ctx.send("Invalid page")
            await asyncio.sleep(3)
            await message.delete()
            return

        # # Connect to the database and select every row
        # db = await aiosqlite.connect("main.db")
        # cursor = await db.execute("SELECT Count(*) FROM exp")

        # # Get the maximum amound of entries
        # max = await cursor.fetchone()
        # max = max[0]
        
        # lower_limit = page * 20
        # upper_limit = lower_limit + 20
        # if upper_limit > max:
        #     upper_limit = max
        # if lower_limit > max:
        #     # Replace this with an actual error raise
        #     await ctx.send("Invalid page.")
        #     return

        # cursor = await db.execute(
        #     f"SELECT user_id,total_exp FROM exp ORDER BY total_exp DESC LIMIT {lower_limit},{20}"
        # )
        
        # await cursor.close()
        # await db.close()

        # Replace this with a call to the database class
        #rows = await cursor.fetchall()
        
        rows = await database.top("total_exp", "exp", page, ctx)

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
            title=f"{self.avo_cult.name} temp top 20", description=descript
        )
        embed.set_footer(
            text=f"Page {page + 1} - Type /top {page + 2} to get page {page + 2} of the leaderboard"
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def addexp(self, ctx, member: discord.Member, exp: int):
        await ctx.trigger_typing()
        if await database.look_for_user(member.id, "exp"):
            old_exp = await database.retrieve("exp", "text", member.id)
            new_exp = old_exp + exp
            await database.update("exp", "text", new_exp, member.id)
            await ctx.send(f"{member.name} now has {new_exp} Text EXP")
        else:
            await ctx.send(
                "That person wasn't registered in the database previously, but they are now.\nRun the command again to set their exp."
            )


def setup(bot):
    bot.add_cog(Leveler(bot))