import discord 
from discord.ext import commands
import asyncio
import ffmpeg
import spotdl
from youtube_dl import YoutubeDL
import os
import time
import nest_asyncio
from dotenv import load_dotenv
import requests


startTime = time.time()

load_dotenv()


queued = []
nest_asyncio.apply()
SDL = spotdl.Spotdl(client_id=str(os.getenv('SPOTIFY_CLIENT')), client_secret=str(
    os.getenv('SPOTIFY_SECRET')), headless=True, downloader_settings={"output": "./music/{artists} - {title}.{output-ext}"}, loop=asyncio.get_event_loop())


async def queuer(ctx, queued, interaction, embed):
    FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    await interaction.edit_original_response(embed=embed)
    voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    voice.stop()
    while len(queued) > 0:
        voice.play(discord.FFmpegPCMAudio(queued[0], **FFMPEG_OPTS), after=lambda e: print('done', e))
        #voice.play(discord.FFmpegPCMAudio(source=queued[0]))
        voice.source = discord.PCMVolumeTransformer(
            original=voice.source, volume=0.25)
        length = float(ffmpeg.probe(queued[0])['format']['duration'])
        queued.pop(0)
        await asyncio.sleep(length)


async def playc(ctx, search, queued, SDL, skip):

    if skip:
        embed = discord.Embed(color=0xfee9b6, title="⏳  Loading...")
        interaction = await ctx.respond(embed=embed)

        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

        if not voice:
            embed = discord.Embed(color=0xdd2f45, title="❌  MEGABOT Is Not In Voice").set_thumbnail(
                url="https://raw.githubusercontent.com/NicPWNs/MEGABOT/main/images/thumbnail.gif")
            await interaction.edit_original_response(embed=embed)

        else:
            embed = discord.Embed(color=0x5daced, title="⏭️  Skipping Song!")
            await queuer(ctx, queued, interaction, embed)

    else:
        embed = discord.Embed(color=0xfee9b6,
                              title="⏳  Downloading...",
                              description=f"**Request:** \"{search}\""
                              )

        interaction = await ctx.respond(embed=embed)

        if not ctx.author.voice:
            embed = discord.Embed(color=0xdd2f45,
                                  title="❌  Error",
                                  description=f"<@{ctx.user.id}> is not connected to a voice channel!"
                                  ).set_thumbnail(url=ctx.user.display_avatar)

            await interaction.edit_original_response(embed=embed)
            return

        channel = ctx.author.voice.channel

        try:
            voice = await channel.connect()
        except:
            voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            await voice.move_to(channel)

        if "http" in search:
            if "youtube.com" in search:
                ydl_opts = {
                    'skip_download': True,
                    'noplaylist': True,
                    'quiet': True,
                    'no_warnings': True,
                    'get_title': True
                }
                with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
                    try: requests.get(search)
                    except: info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
                    else: info = ydl.extract_info(search, download=False)
                    path = (info, info['formats'][0]['url'])
                    queued.append(path)

                #with YoutubeDL(ydl_opts) as ydl:
                 #   search = ydl.extract_info(
                  #      search, download=False, process=False)['title']
            elif "spotify.com" in search:
                try:
                    song = SDL.search([search])[0]
                    title = song.name
                    cover = song.cover_url
                    artist = song.artist
                    song, path = SDL.download(song)
                    queued.append(path)
                    print(queued)
            
                except spotdl.types.song.SongError:
                    embed = discord.Embed(color=0xdd2f45,
                                        title="❌  Error",
                                        description=f"**No results found for:** {search}"
                                        ).set_thumbnail(url=ctx.user.display_avatar)
                    await interaction.edit_original_response(embed=embed)
                    return
            else:
                embed = discord.Embed(color=0xdd2f45,
                                      title="❌  Error",
                                      description=f"Only **YouTube** and **Spotify** URLs are Currenty Supported!"
                                      ).set_thumbnail(url=ctx.user.display_avatar)
                await interaction.edit_original_response(embed=embed)
                return


            


        embed = discord.Embed(color=0x5daced,
                              title="🎵  Now Playing",
                              description="{title}"
                              ).set_thumbnail(url="").set_footer(text="by {artist}")

        if not voice.is_playing():
            await queuer(ctx, queued, interaction, embed)
        else:
            embed = discord.Embed(color=0x5daced,
                                  title="↩️  Added to Queue",
                                  description="{title}"
                                  ).set_thumbnail(url="").set_footer(text="by {artist}")

            await interaction.edit_original_response(embed=embed)


async def queue(ctx, queued):

    embed = discord.Embed(color=0xfee9b6, title="⏳  Loading...")
    interaction = await ctx.respond(embed=embed)

    voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

    if not voice:
        embed = discord.Embed(color=0xdd2f45, title="❌  MEGABOT Is Not In Voice").set_thumbnail(
            url="https://raw.githubusercontent.com/NicPWNs/MEGABOT/main/images/thumbnail.gif")
        await interaction.edit_original_response(embed=embed)

    else:
        description = ""
        num = 1

        if len(queued) == 0:
            description = "Queue is empty!"

        else:
            for song in queued:
                description += f"{num}. {os.path.splitext(song)[0]}\n"
                num += 1

        embed = discord.Embed(
            color=0x5daced, title="🔢  Current Queue", description=description)
        await interaction.edit_original_response(embed=embed)
