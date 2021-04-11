import discord
from discord.errors import Forbidden
from discord.ext import commands
from discord.ext.tasks import loop
from discord_slash import SlashCommand

import asyncio
import aiosqlite




# intents = discord.Intents(members=True)
bot = commands.Bot(command_prefix="$")
bot.remove_command("help")
slash = SlashCommand(bot, sync_commands=True)

# The only Guild the bot will work with
avo_cult = None

# Hardcoded Text Channels
report_channel = None
report_channel_id = 785738570207068191

# Roles
# boosters = None
# boosted = None
# boosted_role_id = 731226520680661022


# Donator Monitor
# @loop(hours=24)
# async def dono_monitor():
#     print(boosters)
#     for member in boosters:
#         if boosted not in member.roles:
#             await member.add_roles(boosted, reason="Boosted the Guild")
#             print(f"Gave {member.name} the Server Boosted role")

# @dono_monitor.before_loop
# async def dono_monitor_before():
#     await bot.wait_until_ready()


# Watch for people sending the Ban emote
@bot.event
async def on_message(ctx):
    user = ctx.author

    # Look for ban emoji
    if "<:zBan:818051501020151818>" in ctx.content and not user.bot:
        context = ctx
        await ctx.delete()
        await reaction_report(context, context.author)

    if ctx.channel.id in [698795649054933032, 557869986895495180]:
        await bot.process_commands(ctx)


@bot.event
async def on_ready():
    print("We have logged in as {0.name}, {0.id}".format(bot.user))

    global avo_cult
    avo_cult = bot.get_guild(556972632977965107)
    print(f"Guild recognized as {avo_cult}")

    global report_channel
    report_channel = bot.get_channel(report_channel_id)

    #global boosters
    #global boosted
    #boosters = avo_cult.premium_subscribers # TODO: According to a github issue, this requires the "member intent", this isn't specified on docs afaik. Not really sure what this is or how to implement it, and whenever I do I get rate limited.
    #boosted = avo_cult.get_role(boosted_role_id)


# Error handler for when users send commands too fast
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.trigger_typing()
        message = await ctx.send(
            f"**Cool down!** Wait for just **{int(error.retry_after)}** seconds before you send the next command, okay?"
        )
        await asyncio.sleep(int(error.retry_after))
        await message.delete()
    else:
        await ctx.send(error)


# Ban reaction listener
@bot.event
async def on_raw_reaction_add(payload):
    emoji = payload.emoji
    if payload.emoji == bot.get_emoji(818051501020151818):
        channel_id = payload.channel_id
        channel = await bot.fetch_channel(channel_id)
        message_id = payload.message_id
        message = await channel.fetch_message(message_id)
        member = payload.member
        await message.remove_reaction(emoji, member)
        await reaction_report(message, member, message.author)
        

# Send a report embed
async def reaction_report(message, reporter: discord.User, reported: discord.User = None):
    embed = discord.Embed(title="New React Report")
    if reported != None:
        embed.add_field(
            name="Report Info",
            value=f"""**Reporter:** {reporter.name}#{reporter.discriminator} {reporter.mention}
        **Reported:** {reported.name}#{reported.discriminator} {reported.mention}
        **Channel:** {message.channel.mention}
        [Jump to message]({message.jump_url})
        """
        )
    else:
        embed.add_field(
            name="Report Info",
            value=f"""**Reporter:** {reporter.name}#{reporter.discriminator} {reporter.mention}
        **Channel:** {message.channel.mention}
        [Jump to context]({message.jump_url})
        """
        )
    await report_channel.send(content=f"<@&688140458945150999> <@&562765262172979200>" ,embed=embed)
    try:
        await reporter.send("Your report has been recieved.")
    except Forbidden:
        pass

# Retrieve a value from the database
async def sql_retrieve(table: str, coloumn: str, user_id: int):
    db = await aiosqlite.connect("main.db")
    cursor = await db.execute(
        f"SELECT {coloumn} FROM {table} WHERE user_id = {user_id}"
    )
    try:
        tupled = await cursor.fetchone()
        value = tupled[0]
        await cursor.close()
        await db.close()
        return value
    except TypeError:
        print(f"Getting the value of {coloumn} from {user_id} returned a NoneType.")
        await cursor.close()
        await db.close()
        return None

# Update a value in the database
async def sql_update(table: str, coloumn: str, value: int, user_id: int):
    db = await aiosqlite.connect("main.db")
    await db.execute(
        f"UPDATE {table} SET {coloumn} = {value} WHERE user_id = {user_id}"
    )
    await db.commit()
    await db.close()


# dono_monitor.start()
bot.load_extension("leveler")
bot.load_extension("economy")
bot.run("Njk3NjE1MzQxMDUxODM4NDc1.Xo526g.p9rWXTbh7NIXLDX5bQRzQ9hHBNI")