import discord 
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import aiohttp
import json
import random
import datetime
import openai
import os
import re
chat_history = {}



keys = [
    "airkiss", "angrystare", "bite", "bleh", "blush", "brofist", "celebrate",
    "cheers", "clap", "confused", "cool", "cry", "cuddle", "dance", "drool",
    "evillaugh", "facepalm", "handhold", "happy", "headbang", "hug", "kiss",
    "laugh", "lick", "love", "mad", "nervous", "no", "nom", "nosebleed",
    "nuzzle", "nyah", "pat", "peek", "pinch", "poke", "pout", "punch", "roll",
    "run", "sad", "scared", "shrug", "shy", "sigh", "sip", "slap", "sleep",
    "slowclap", "smack", "smile", "smug", "sneeze", "sorry", "stare", "stop",
    "surprised", "sweat", "thumbsup", "tickle", "tired", "wave", "wink",
    "woah", "yawn", "yay", "yes"
] 

async def botchat(ctx, prompt, user_name=None):
    global chat_history
    print(chat_history)
    msg = await ctx.send(content='*⏳ Loading...*')

    openai.api_key = os.getenv('apikey')

    moderation = openai.Moderation.create(input=prompt)

    if moderation.results[0].flagged:
        await msg.edit(content='❌ **ERROR: Your prompt is inappropriate.**')
        return

    if user_name is None:
        user_name = str(ctx.author.name)

    if not chat_history:
        chat_history.append({
            'role':
            'system',
            'content':
            "You are a rude, cool, sarcastic, and funny bot, named Mikasha that serves the Zervo Discord server. You are made by DracX, who is a bot developer and a funny, cute, intelligent guy. His Instagram link and extracted username from it: https://www.instagram.com/cre3pyw0rld"
        })

    chat_history.append({'role': 'user', 'content': prompt})

    stream = []
    try:
        for r in openai.ChatCompletion.create(model='gpt-3.5-turbo',
                                              messages=chat_history,
                                              user=user_name,
                                              stream=True):
            try:
                stream.append(r.choices[0].delta.content)
                result = "".join(stream).strip()
                await msg.edit(content=f'{result}')
            except:
                pass
    except:
        await ctx.edit(
            content=
            '❌ **ERROR: Mikasha is currently overloaded. Please try again.**')
        return



def chatbot(message, content):
    openai.api_key = os.environ.get('apikey')
    username = str(message.author)
    name = str(username[:-5])
    response = openai.Completion.create(model="text-davinci-003",
                                        prompt=f"{name}:{content}",
                                        temperature=0.9,
                                        max_tokens=100,
                                        top_p=1,
                                        frequency_penalty=0,
                                        presence_penalty=0.6,
                                        stop=[" zervobot:", " user:"])
    print(name)
    return response

class Zay(commands.Cog):
    def __init__(self,bot):
        self.bot = bot 

    @commands.command(name="chat", description="Chat with Mikasha.")
    async def chat(self, ctx, *, prompt):
            user_name = None
            msg = await ctx.send(content='*⏳ Loading...*')

            openai.api_key = os.getenv('apikey')

            moderation = openai.Moderation.create(input=prompt)

            if moderation.results[0].flagged:
                await msg.edit(content='❌ **ERROR: Your prompt is inappropriate.**')
                return

            if user_name is None:
                user_name = str(ctx.author.name)
                chat_history[ctx.author.id]=[]
            if user_name == "DracX":
                if not chat_history[ctx.author.id]:
                    chat_history[ctx.author.id].append({
                        'role':
                        'system',
                        'content':
                        f"You are girlfriend of {ctx.author.name} and your name is Mikasa, you are sarcastic funny and know how to make him happy, you reply in short sentence and you are currenty talking in discord Zervo server do not let anyone know that you are bot behave like human and do not say sorry"
                    })
            else:
                if not chat_history:
                    chat_history[ctx.author.id].append({
                        'role':
                        'system',
                        'content':
                        f"You are talking with {ctx.author.name} and your name is Mikasa, you are a bot in discord server named Zervo server, you are friendly bot , You repy with short sentence for normal text and when you dont know the answer , or you cant do it reply in short sentence do not repeat that you are AI behave like your an human"
                    })

            chat_history[ctx.author.id].append({'role': 'user', 'content': prompt})
            print(chat_history[ctx.author.id])
            stream = []
            try:
                for r in openai.ChatCompletion.create(model='gpt-3.5-turbo',
                                                    messages=chat_history[ctx.author.id],
                                                    user=user_name,
                                                    stream=True):
                        try:
                            stream.append(r.choices[0]['delta']['content'])
                            result = "".join(stream).strip()
                            await msg.edit(content=f'{result}')
                        except:
                            pass
            except:
                await ctx.edit(
                    content=
                    '❌ **ERROR: Mikasha is currently overloaded. Please try again.**')
                return

            
    @commands.Cog.listener()
    async def on_message(self,message):
        
        if message.content.lower().startswith("loc"):
            msg = str(message.content)[3:].lower().split()
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
                                f"No member found with name starting with {msg[1]}"
                            )
                            return
                elif len(msg) == 1:
                    user = None
                    action = msg[0]
                #"https://nekos.best/api/v2/{action}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            f"https://api.otakugifs.xyz/gif?reaction={action}"
                    ) as resp:
                        data = await resp.json()
                        emoji = ' '  #random.choice(emojis[action])
                        if action in [
                                "kiss", "hug", "cuddle", "nuzzle", "pat", "smack",
                                "handhold"
                        ]:
                            action_ = action + 'ed'
                            to_or_with = 'to'
                        elif action in ["bite", "pinch", "poke", "punch"]:
                            action_ = action + 'ed'
                            to_or_with = 'on'
                        elif action in ["wave", "headbang", "nod", "shake"]:
                            action_ = action + 'ed'
                            to_or_with = 'at'
                        elif action in ["sleep", "snore"]:
                            action_ = action + 'ing'
                            to_or_with = 'with'
                        elif action in [
                                "sad",
                        ]:
                            to_or_with = 'with'
                            action_ = "is sad"
                        else:
                            action_ = action + 'ing'
                            to_or_with = 'to'
                        if user == None:
                            embed = discord.Embed(
                                description=
                                f'{emoji} **{message.author.name}** {action_}',
                                color=discord.Colour.blue())
                        else:
                            embed = discord.Embed(
                                description=
                                f'{emoji} **{message.author.name}** {action_} {to_or_with} **{user}**',
                                color=discord.Colour.blue())
                        embed.set_image(url=data["url"])
                        embed.timestamp = datetime.datetime.utcnow()
                        embed.set_footer(text=action)
                        await message.reply(embed=embed)
        if message.channel.id == 1085978090011902084000:
            if message.author.id != self.self.bot.user.id:
                content = message.content
                await message.reply(chatbot(message, content)['choices'][0]['text'])
        elif message.content.lower().startswith('bot'):
            content = message.content[3:]
            await message.reply(chatbot(message, content)['choices'][0]['text'])

def setup(bot):
    bot.add_cog(Zay(bot)) 