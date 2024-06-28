import discord 
from discord.ext import commands
import asyncio
import ffmpeg
import spotdl
fr
import os
import time

from dotenv import load_dotenv
from cogs.Musics import playc,queue,queued,SDL
import requests

def Search(query):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
        try: requests.get(query)
        except: info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        else: info = ydl.extract_info(query, download=False)
    return (info, info['formats'][0]['url'])

async def join(ctx, voice):
    channel = ctx.author.voice.channel

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect() 

class Music(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @commands.command(name="play", description="Plays music.")
    async def _play(self,ctx, search):
        channel = ctx.author.voice.channel
        try:
            voice = await channel.connect()
        except:
            voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            await voice.move_to(channel)
        FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        video, source = Search(search)
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        await join(ctx, voice)
        await ctx.send("dfgd")
        voice.play(discord.FFmpegPCMAudio(source, **FFMPEG_OPTS), after=lambda e: print('done', e))

    @commands.command(name="queue", description="Show the current music queue.")
    async def call(self,ctx):
        await queue(ctx, queued)
    
    @commands.command(name="skip", description="Skip the current song.")
    async def call(self,ctx):
        channel = ctx.author.voice.channel
        try:
            voice = await channel.connect()
        except:
            voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            await voice.move_to(channel)
        await ctx.send("skiping...")
        voice.stop()


def setup(bot):
    bot.add_cog(Music(bot))