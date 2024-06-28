import discord
from discord import option
from discord.ext import commands
import requests
import json
from bs4 import BeautifulSoup
import re
import datetime
from utils.configs import colors

channels = []


def is_allowed(ctx):
  allowed_user_id = 632748789341618207
  if ctx.author.guild_permissions.administrator or ctx.author.id == allowed_user_id:
    return True
  else:
    return False


class Globalchat(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.slash_command(name="gc_channel",
                          description="Connects server chats")
  async def _gc_channel(self, ctx, channel: discord.TextChannel):
    if is_allowed(ctx):
      global channels
      channely = self.bot.db.execute("select * from globalchat where gId = ?",
                                     (ctx.guild.id, )).fetchall()

      if channely:
        self.bot.db.execute(
          "update globalchat set cId = ?, cName = ? where gId = ?",
          (channel.id, channel.name, ctx.guild.id))
        self.bot.conn.commit()
        gc = self.bot.db.execute(
          "select cId from globalchat where active = 1").fetchall()
        channels = []
        for channelx in gc:
          channels.append(channelx[0])
        await ctx.respond(
          f"Successfully set **Globalchat** channel to {channel.mention}")
      else:
        print(channel)
        self.bot.db.execute(
          "insert into globalchat values (?,?,?,?,?)",
          (ctx.author.id, ctx.guild.id, channel.id, 1, channel.name))
        self.bot.conn.commit()
        gc = self.bot.db.execute(
          "select cId from globalchat where active = 1").fetchall()
        channels = []
        for channelx in gc:
          channels.append(channelx[0])
        await ctx.respond(
          f"Successfully set **Globalchat** channel to {channel.mention}")
    else:
      await ctx.respond(
        f"{ctx.author.mention}, you need adminitrator permission to run this command",
        ephemeral=True)

  @commands.slash_command(name="globalchat",
                          description="Enable/desable globalchat")
  @option("status", description="Choose status", choices=["enable", "disable"])
  async def _globalchat(self, ctx: discord.ApplicationContext, status):
    if is_allowed(ctx):
      
      await ctx.respond(status)
    else:
      await ctx.respond(
        f"{ctx.author.mention}, you need adminitrator permission to run this command",
        ephemeral=True)

  @_globalchat.error
  async def _globalchat_handler(self, ctx, error):
    if isinstance(error, commands.MissingPermissions):
      await ctx.respond(
        f"{ctx.author.mention}, only user with admin permission can run this command"
      )

  @commands.Cog.listener()
  async def on_message(self, message):
    global channels
    print(channels)
    if not channels:
      gc = self.bot.db.execute(
        "select cId from globalchat where active = 1").fetchall()
      for channel in gc:
        print(channel)
        channels.append(channel[0])

    if message.author.bot:
      return
    if message.channel.id in channels:
      for channel_id in channels:
        for guild in self.bot.guilds:
          target_channel = discord.utils.get(guild.text_channels,
                                             id=channel_id)
          if target_channel:
            if target_channel.id != message.channel.id:
              msg = ''
              desc = message.content
              user = await self.bot.fetch_user(message.author.id)
              banner_clr = user.accent_color
              if banner_clr == None:
                banner_clr = colors["DARK_GREY"]

              if desc.startswith("https://tenor"):
                response = requests.get(desc)
                html_content = response.text
                soup = BeautifulSoup(html_content, 'lxml')
                img = soup.find('meta', property='og:image')['content']
                title = soup.find('meta', property='og:title')['content']
                embed = discord.Embed(description=title, color=banner_clr)
                embed.set_image(url=f"{img}")
              else:
                pattern = re.compile(r'(https?://\S+)', re.IGNORECASE)
                matches = pattern.findall(desc)

                for link in matches:
                  desc = desc.replace(f"{link}", f"[link]({link})")
                embed = discord.Embed(description=f"{desc}", color=banner_clr)
                img = ""
                if message.attachments:
                  img = message.attachments[0].url
                elif matches:
                  if matches[0].endswith("png") or matches[0].endswith(
                      "jpeg") or matches[0].endswith("jpg") or matches[
                        0].endswith("gif") or matches[0].endswith("webp"):
                    img = matches[0]
                if img:
                  embed.set_image(url=img)

              embed.set_author(name=message.author,
                               icon_url=message.author.avatar)
              if message.reference:
                m_obj = await message.channel.fetch_message(
                  message.reference.message_id)
                try:
                  emb = m_obj.embeds[0]
                  embed.set_footer(
                    text=
                    f"Replied to {emb.author.name}: {emb.description[:15]}|{m_obj.guild.name}",
                    icon_url=f"{emb.author.icon_url}")
                except:
                  embed.set_footer(
                    text=
                    f"Replied to {m_obj.author.name}: {m_obj.content[:15]} | {m_obj.guild.name}",
                    icon_url=f"{m_obj.author.avatar}")
              else:
                embed.set_footer(text=f"{message.guild.name}",
                                 icon_url=f"{message.guild.icon}")
              embed.timestamp = datetime.datetime.utcnow()
              await target_channel.send(embed=embed)
              await message.add_reaction("✅")


def setup(bot):
  bot.add_cog(Globalchat(bot))
