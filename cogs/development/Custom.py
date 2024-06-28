import discord 
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import json
import random
import datetime
import re

db =  {}
count = 1
keys = ["airkiss","angrystare","bite","bleh","blush","brofist","celebrate","cheers","clap","confused","cool","cry","cuddle","dance","drool","evillaugh","facepalm","handhold","happy","headbang","hug","kiss","laugh","lick","love","mad","nervous","no","nom","nosebleed","nuzzle","nyah","pat","peek","pinch","poke","pout","punch","roll","run","sad","scared","shrug","shy","sigh","sip","slap","sleep","slowclap","smack","smile","smug","sneeze","sorry","stare","stop","surprised","sweat","thumbsup","tickle","tired","wave","wink","woah","yawn","yay","yes"]


def KeySearch(userid):
    global db
    global count
    data = db[userid]
    listx = [x for x in data]
    rdata = listx[count]
    ddata = listx[count-1]
    count += 1
    url = rdata['murl']
    ourl = ddata['murl']
    odesc = re.sub('[^a-zA-Z ]+', '',ddata['t'])
    desc = re.sub('[^a-zA-Z ]+', '',rdata['t'])
    print(count)
    return [url,desc,ourl,odesc]

class MyView(discord.ui.View):

    def __init__(self, bot, ctx,keyword,if_mention,if_none, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.ctx = ctx
        self.if_mention = if_mention
        self.if_None = if_none
        self.keyword = keyword

    @discord.ui.button(label='yes', style=discord.ButtonStyle.primary , emoji='✅')
    async def button_callback2(self, button, interaction):
        global db
        c = self.bot 
        data = KeySearch(self.ctx.author.id)
        c.db.execute("insert into reactions (dId,keyword,desc,link,if_mention,if_None) values(?,?,?,?,?,?)",(interaction.user.id,self.keyword,data[3],data[2],self.if_mention,self.if_None))
        c.conn.commit()
        embed = discord.Embed(description=f"Press **Yes** if image match with keyword **{self.keyword}**\n\n Else **No** \n**Do not Wrong vote**\n\n")
        embed.set_image(url=data[0])
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label='No',style=discord.ButtonStyle.primary, emoji="❎")
    async def button_callback(self, button, interaction):
        global db
        data = db[self.ctx.author.id]
        data = KeySearch(self.ctx.author.id)
        embed = discord.Embed(description=f"Press **Yes** if image match with keyword **{self.keyword}**\n\n Else **No** \n**Do not Wrong vote**\n\n")
        embed.set_image(url=data[0])
        await interaction.response.edit_message(embed=embed)


class Custom(commands.Cog):
    def __init__(self,bot):
        self.bot = bot 
    @commands.slash_command(name ='add')
    async def _add(self,ctx,query,keyword,if_mention,if_none):
        keyword = keyword.split()[0]
        if keyword in keys:
            await ctx.respond(f"{keyword} Already exists")
            return
        if "author" and "mention" not in if_mention:
            await ctx.respond("**if_mention** must contain word 'author' and 'mentiion'\n**Example** author kissing to mention\n")
            return
        if "author" not in if_none:
            await ctx.respond("**if_none** must contain word 'author'\n**Example** author kissing\n")
            return
        data = []
        global db
        url = f"https://www.bing.com/images/search?q={query}"
        custom_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"

        res = requests.get(url, headers={
            "User-Agent": custom_user_agent,
        })
        soup = BeautifulSoup(res.content, 'lxml')
        for a in soup.find_all("a", {"class": "iusc"}):
            m = json.loads(a["m"])
            murl = m["murl"]
            data.append(m)
        url = data[0]['turl']
        view = MyView(self.bot, ctx,keyword,if_mention,if_none)
        if data:
            db[ctx.author.id]=data
            embed = discord.Embed(title='Add keyword',description=f'Press **Yes** if image match with keyword **{keyword}**\n\n Else **No** \n**Do not Wrong vote**\n\n')
            embed.set_image(url=url)
            await ctx.respond(embed=embed, view=view)
        else:
            await ctx.respond(f"[{query} ] may contain banned words")


    @commands.Cog.listener()
    async def on_message(self,message):
        links = []
        if message.content.lower().startswith("loc"):
            msg = str(message.content)[3:].lower().split()
            found_member = False
            if not msg:
                return
            cmd = msg[0]
            keywords = []
            lkeywords = self.bot.db.execute('select DISTINCT keyword from reactions').fetchall()
            for x in lkeywords:
                keywords.append(x[0])
            if cmd in keywords:
                data = self.bot.db.execute("select * from reactions where keyword = ?",(cmd,)).fetchall()
                img = random.choice(data)
                print(img)
                if len(msg) >= 2:
                    action = msg[0]
                    user = msg[1]
                    if user.startswith("<@"):
                        dec = int(user.replace("<@", "").replace('>', ""))
                        duser = self.bot.get_user(dec)
                        user = duser.name
                        pass
                    elif user == 'random':
                        user = random.choice([name.name for name in message.guild.members])
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
                if user==None:
                    mes = img[6]
                    print(mes)
                    text = mes.replace("author",message.author.name)
                    embed = discord.Embed(description=text)
                else:
                    mes = img[5]
                    print(mes)
                    text = mes.replace('author',message.author.name).replace('mention',user)
                    embed = discord.Embed(description=text)
                embed.set_image(url=img[4])
                await message.reply(embed=embed)

def setup(bot):
    bot.add_cog(Custom(bot)) 