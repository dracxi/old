import discord
from discord.ext import commands
import requests
import json
from bs4 import BeautifulSoup
import datetime
import re
from main import colors
import random
import aiohttp
from utils.configs import command_dict, keys, prefix2

x = [
    "airkiss", "angrystare", "bite", "bleh", "blush", "brofist", "celebrate",
    "cheers", "clap", "confused", "cool", "cry", "cuddle", "dance", "drool",
    "evillaugh", "facepalm", "handhold", "happy", "headbang", "hug", "kiss",
    "laugh", "lick", "love", "mad", "nervous", "no", "nom", "nosebleed",
    "nuzzle", "nyah", "pat", "peek", "pinch", "poke", "pout", "punch", "roll",
    "run", "sad", "scared", "shrug", "shy", "sigh", "sip", "slap", "sleep",
    "slowclap", "smack", "smile", "smug", "sneeze", "sorry", "stare", "stop",
    "surprised", "sweat", "thumbsup", "tickle", "tired", "wave", "wink", "woah",
    "yawn", "yay", "yes"
]


class Interactions(
    commands.Cog,
    description=f"**Ineraction command**\n*Example*: {prefix2} cry [user mention or nickname] \n**Prefix**:{prefix2}"
):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="interaction_commands",
                            description="List of all interaction commands")
    async def test(self, ctx):
        command_list = []
        print(keys)
        print(len(keys))
        count = 0
        for cmd in keys:
            command_list.append(f"`{cmd}` ,")
        value = f"".join([f"{x}" for x in command_list])
        embed = discord.Embed(
            title="Interaction command list",
            description="`miko` [command] [(optional @user or nickname)]")
        embed.add_field(name="Commands", value=value)
        embed.add_field(
            name="Errors",
            value="This command is under development, you may see grammatical errors because im using algorithm instead of typing them separatly\nSo kindly report me when you see"
        )
        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower().startswith(prefix2):
            msg = str(message.content)[4:].lower().split()
            found_member = False
            if not msg:
                return
            cmd = msg[0]
            if cmd in keys:
                if len(msg) >= 2:
                    action = msg[0]
                    user = msg[1]
                    if user.startswith("<@"):
                        dec = int(user.replace("<@", "").replace('>', ""))
                        duser = self.bot.get_user(dec)
                        user = duser.name
                        pass
                    elif user == 'random':
                        user = random.choice(
                            [name.name for name in message.guild.members])
                    else:
                        for name in message.guild.members:
                            if name.name.lower().startswith(user) or \
                                    (name.nick is not None and name.nick.lower().startswith(user)):
                                user = name.name
                                found_member = True
                                break
                            else:
                                continue
                            break
                        if not found_member:
                            await message.reply(
                                f"No member found with name starting with {msg[1]}")
                            return
                elif len(msg) == 1:
                    user = None
                    action = msg[0]
                # "https://nekos.best/api/v2/{action}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            f"https://api.otakugifs.xyz/gif?reaction={action}") as resp:
                        data = await resp.json()
                        emoji = ' '  # random.choice(emojis[action])
                        if action in [
                            "kiss", "hug", "cuddle", "nuzzle", "pat", "smack", "handhold"
                        ]:
                            action_ = action + 'ed'
                            to_or_with = 'to'
                        elif action in ["bite", "pinch", "poke", "punch", 'thumbsup']:
                            action_ = action + 'ed'
                            to_or_with = 'on'
                        elif action in ["wave", "headbang", "nod", "shake"]:
                            action_ = action + 'ed'
                            to_or_with = 'at'
                        elif action in ["sleep", "snore", "cry"]:
                            action_ = action + 'ing'
                            to_or_with = 'with'
                        elif action in ["sad", "tired", "mad"]:
                            to_or_with = 'with'
                            action_ = f"is {action}"
                        elif action in ["yes"]:
                            to_or_with = 'with'
                            action_ = "is agree"
                        elif action in ["woah", "yawn", "yay"]:
                            to_or_with = ''
                            action_ = action
                        elif action in ["sneeze", "cough", "nervous"]:
                            action_ = action + 'ing'
                            to_or_with = 'about'
                        else:
                            action_ = action + 'ing'
                            to_or_with = 'to'

                        if user == None:
                            embed = discord.Embed(
                                description=f'{emoji} **{message.author.name}** {action_}',
                                color=discord.Colour.blue())
                        else:
                            embed = discord.Embed(
                                description=f'{emoji} **{message.author.name}** {action_} {to_or_with} **{user}**',
                                color=discord.Colour.blue())
                        embed.set_image(url=data["url"])
                        embed.timestamp = datetime.datetime.utcnow()
                        embed.set_footer(text=action.capitalize())
                        await message.reply(embed=embed)


def setup(bot):
    bot.add_cog(Interactions(bot))
