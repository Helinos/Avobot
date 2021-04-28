import asyncio
import os
import random

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option
from utils import error

radio_channel: discord.VoiceChannel = None
avo_cult: discord.Guild = None
songs: list = []
_song = None

stations: dict = {
    "poolside": ["81.3 Poolside FM", "local"],
    "tokyo": ["82.9 Tokyo Disco", "local"],
    "friday": ["84.7 It's Friday Somewhere", "local"],
    "lofi": ["86.3 Hangover Club", "local"],
    "80s": ["88.5 Underground 80s", "stream", "http://ice4.somafm.com/u80s-256-mp3"],
    "drone": ["94.1 Drone Zone", "stream", "http://ice6.somafm.com/dronezone-256-mp3"],
    "drill": ["94.3 London Undergound", "local"],
    "vaporwave": ["96.5 Vapor FM", "stream", "http://ice4.somafm.com/vaporwaves-128-mp3"],
    "sega": ["97.1 Radio SEGA", "stream", "http://content.radiosega.net:8006/rs-mpeg.mp3"],
    "eurobeat": ["97.3 Cool Vibrations", "local"],
    "darksynth": ["97.5 Heli Hymns", "local"],
    "rancheras": ["101.9 Rancheras", "local"],
    "space": ["103.7 Deep Space One", "stream", "http://ice2.somafm.com/deepspaceone-128-mp3"],
    "metal": ["103.9 Metal Detector", "stream", "http://ice2.somafm.com/metal-128-mp3"],
    "celtic": ["104.3 Thistle Radio", "stream", "http://ice4.somafm.com/thistle-128-mp3"],
    "country": ["104.7 Boot Liquor", "stream", "http://ice6.somafm.com/bootliquor-320-mp3"],
    "rock": ["105.1 Rock Paradise", "stream", "https://stream.radioparadise.com/rock-320"], 
    "funny": ["420.69 Funnie FM", "local"],
}

_station: str = None


class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.interupt = False

    @commands.Cog.listener()
    async def on_ready(self):
        global radio_channel
        radio_channel = await self.bot.fetch_channel(833262817859076109)
        global avo_cult
        avo_cult = self.bot.get_guild(556972632977965107)
        global _station
        _station = "poolside"

        # Join the Radio channel
        if avo_cult.voice_client is not None:
            return await avo_cult.voice_client.move_to(radio_channel)
        await radio_channel.connect()

        for file in os.listdir(f"./music/{_station}/"):
            songs.append(file)

        random.shuffle(songs)
        first_song = songs.pop(0)
        self.play_song(first_song, "local")

    def play_song(self, song, station_type):
        """Plays a file from the current station"""
        
        if station_type == "local":
            def after_playing(err):
                # If the music has been manually interupted
                if not self.interupt:
                    print("play_song: Playing next song")
                    random.shuffle(songs)
                    next_song = songs[0]
                    print(f"play_song: next_song = {next_song}")
                    songs.append(song)
                    self.play_song(next_song, "local")
                else:
                    print("play_song: Song interupted. Stopping song.")
                    self.interupt = False

                if err != None:
                    print(err)

            global _song
            _song = song
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(f"./music/{_station}/{song}"), 0.10
            )
            avo_cult.voice_client.play(source, after=after_playing)

        elif station_type == "stream":
            self.interupt = False
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(song), 0.10
            )
            avo_cult.voice_client.play(source)

    
    # Sends an embed with the top twenty users ordered by total balance
    @cog_ext.cog_slash(
        name="station",
        description="Vote to change the Radio's current Station.",
        options=[
            create_option(
                name="station",
                description="The station you want to initiate a vote for",
                option_type=3,
                required=True,
            )
        ],
    )
    async def station_slash(self, ctx, station: str):
        if ctx.channel.id == 557860634927169536:
            await self.station_command(ctx, station)
        else:
            await error(ctx, f"You cannot do that command here")

    @commands.command(name="station")
    async def station_prefix(self, ctx, station: str):
        if ctx.channel.id == 557860634927169536:
            await ctx.trigger_typing()
            await self.station_command(ctx, station)
        else:
            await error(ctx, f"You cannot do that command here")
    
    @commands.command()
    async def station_command(self, ctx, station):
        """Changes the current station"""
        if station in list(stations.keys()):
            self.interupt = True
            avo_cult.voice_client.stop()

            # Play station change static
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(f"./music/static/{random.randint(1,3)}.mp3"), 0.07
            )
            
            await ctx.send(f"Changing the station to {stations[station][0]}.")
            self.interupt = False
            
            if stations[station][1] == "local":
                global _station
                _station = station
                global songs
                songs = []
                for file in os.listdir(f"./music/{_station}/"):
                    songs.append(file)
                random.shuffle(songs)
                first_song = songs.pop(0)

                def after_playing(err):
                    self.play_song(first_song, "local")
            
            elif stations[station][1] == "stream":
                def after_playing(err):
                    self.play_song(stations[station][2], "stream")

            avo_cult.voice_client.play(source, after=after_playing)

        else:
            await ctx.send(f"{station} is not a valid station.")


    @cog_ext.cog_slash(
        name="list",
        description="View the list of avaiable stations.",
    )
    async def station_slash(self, ctx):
        if ctx.channel.id == 557860634927169536:
            await self._station_list(ctx)
        else:
            await error(ctx, f"You cannot do that command here")

    @commands.command(name="list")
    async def station_list(self, ctx):
        if ctx.channel.id == 557860634927169536:
            await ctx.trigger_typing()
            await self._station_list(ctx)
        else:
            await error(ctx, f"You cannot do that command here")

    async def _station_list(self, ctx):
        """Sends a list of all available radio stations"""
        descript: str = ""
        for key in stations.keys():
            descript = descript + f"{key} - **{stations[key][0]}**\n"

        embed = discord.Embed(
            title="Stations",
            description=descript
        )

        await ctx.send(embed=embed)


    @cog_ext.cog_slash(
        name="np",
        description="View the name of the song that's currently playing on the radio.",
    )
    async def np_slash(self, ctx):
        if ctx.channel.id == 557860634927169536:
            await self.np_command(ctx)
        else:
            await error(ctx, f"You cannot do that command here")
    
    @commands.command(name="np")
    async def np_prefix(self, ctx):
        if ctx.channel.id == 557860634927169536:
            await ctx.trigger_typing()
            await self.np_command(ctx)
        else:
            await error(ctx, f"You cannot do that command here")
    
    async def np_command(self, ctx):
        """Sends the name of the song that's currently playing"""

        if stations[_station][1] == "local":
            await ctx.send(f"Now playing: {_song[:-4]}")
        else:
            await ctx.send("Sorry, I can't tell what song is playing on this station yet.")

    @commands.command(name="skip")
    @commands.is_owner()
    async def stop(self, ctx):
        await ctx.send("Sure.")
        avo_cult.voice_client.stop()

def setup(bot):
    bot.add_cog(Radio(bot))
