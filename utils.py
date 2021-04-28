import discord
import asyncio

async def error(ctx, message, status_message: discord.Message = None):
    if status_message != None:
        await status_message.delete()
    error = await ctx.send(message)
    await asyncio.sleep(3)
    await error.delete()