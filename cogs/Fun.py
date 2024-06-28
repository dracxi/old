from time import sleep
import discord
import asyncio
import random
import requests
from discord.ext import commands, tasks
from discord import option
from bs4 import BeautifulSoup
import json
import openai
import aiohttp
import datetime

db = {}
guild = 1031033900547448862
keywords = ['handkiss']


def save(links):
  with open("response.py", "w") as f:
    f.write(links)


class MyView(discord.ui.View):

  def __init__(self, bot, ctx, caption, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.bot = bot
    self.ctx = ctx
    self.caption = caption

  async def on_timeout(self):
    self.disable_all_items()
    await self.message.edit(content="", view=self)

  @discord.ui.button(style=discord.ButtonStyle.primary, emoji="◀")
  async def button_callback2(self, button, interaction):
    global db
    if interaction.user.id != self.ctx.author.id:
      await interaction.response.send_message(
        content="You are not author of this message", ephemeral=True)
      return
    db[self.ctx.author.id][1] -= 1
    count = db[self.ctx.author.id][1]
    links = db[self.ctx.author.id][0]

    embed = discord.Embed(description=f"{self.caption} {count}/{len(links)}",
                          color=discord.Colour.blue())
    embed.set_image(url=links[count])
    await interaction.response.edit_message(embed=embed)

  @discord.ui.button(style=discord.ButtonStyle.primary, emoji="▶")
  async def button_callback(self, button, interaction):
    global db
    if interaction.user.id != self.ctx.author.id:
      await interaction.response.send_message(
        content="You are not author of this message", ephemeral=True)
      return
    db[self.ctx.author.id][1] += 1
    count = db[self.ctx.author.id][1]
    links = db[self.ctx.author.id][0]

    embed = discord.Embed(description=f"{self.caption} {count}/{len(links)}",
                          color=discord.Colour.blue())
    embed.set_image(url=links[count])
    await interaction.response.edit_message(embed=embed)


class Fun(commands.Cog, description="Fun commands"):

  def __init__(self, bot):
    self.bot = bot

  @commands.slash_command(name="coinflip", description="Flip a coin and bet")
  @option("bet", description="Bet on", choices=["Heads", "Tails"])
  async def _flipcoin(self, ctx: discord.ApplicationContext, bet):
    coin = random.choice(["Heads", "Tails"])
    embed = discord.Embed(title=f"{ctx.author.name} fliped a coin",
                          description=f"{coin} 🪙")
    if bet == coin:
      result = "Won 🏆"
    else:
      result = "Lost 👎🏼"
    embed.add_field(name="Result", value=f"You {result}")
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_footer(text=f"Coinflip", icon_url=f"{ctx.author.avatar}")
    await ctx.respond(embed=embed)

  @commands.slash_command(name="hack", description='Hack someone')
  async def _hack(self, ctx, user: discord.Member):
    msg = await ctx.respond(f'hacking {user.name}')
    await asyncio.sleep(3.0)
    await msg.edit_original_response(content='Finding IP address')
    await asyncio.sleep(3.0)
    await msg.edit_original_response(content='IP : 192.168.12.3')
    await asyncio.sleep(3.0)
    await msg.edit_original_response(content='Finding user email address')
    await asyncio.sleep(3.0)
    await msg.edit_original_response(
      content=f'user email: {user.name}@discord.com')
    await asyncio.sleep(1)
    await msg.edit_original_response(
      content=f'Succesessfuly hacked {user.mention}')

  @commands.slash_command(name='waifu', description='Random waifu pics/gif')
  @option("catagory",
          description="Choose chatagory",
          choices=["cuddle", "neko", "shinobu", 'megumin', 'bully', 'waifu'])
  async def _waifu(self, ctx: discord.ApplicationContext, catagory=None):
    if catagory == None:
      catagory = 'waifu'
    res = requests.get(f'https://api.waifu.pics/sfw/{catagory}')
    url = res.json()
    await ctx.respond(url['url'])

  @commands.slash_command(name='nsfwwaifu', description='Random nsfw pics/gif')
  @option("catagory",
          description="Choose chatagory",
          choices=["waifu", "neko", 'trap', 'blowjob'])
  @commands.is_nsfw()
  async def _nsfwwaifu(self, ctx: discord.ApplicationContext, catagory=None):
    if catagory == None:
      catagory = 'waifu'
    res = requests.get(f'https://api.waifu.pics/nsfw/{catagory}')
    url = res.json()
    await ctx.respond(url['url'], delete_after=1000)

  @_nsfwwaifu.error
  async def _nsfwwaifu_handler(self, ctx, error):
    if isinstance(error, commands.NSFWChannelRequired):
      await ctx.respond(f"{ctx.author.mention} Use it on nsfw channel hornyass"
                        )

  @commands.slash_command(name="image", description='Image search')
  async def _image(self, ctx, query, caption: str = None):
    global db
    links = []
    url = f"https://www.bing.com/images/search?q={query}&safesearch=off"
    custom_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"

    res = requests.get(url, headers={
      "User-Agent": custom_user_agent,
    })
    soup = BeautifulSoup(res.content, 'lxml')
    for a in soup.find_all("a", {"class": "iusc"}):
      m = json.loads(a["m"])
      murl = m["murl"]
      links.append(murl)
    if caption == None:
      view = MyView(self.bot, ctx, caption=" ", timeout=60)
    else:
      view = MyView(self.bot, ctx, caption, timeout=60)
    if links:
      db[ctx.author.id] = [links, 1]
      embed = discord.Embed(description=caption, color=discord.Colour.blue())
      embed.set_image(url=links[0])
      await ctx.respond(embed=embed, view=view)
    else:
      await ctx.respond(f"[{query} ] may contain banned words")


def setup(bot):
  bot.add_cog(Fun(bot))
