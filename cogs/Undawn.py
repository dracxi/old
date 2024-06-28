import discord
from discord import option
from discord.ext import commands, tasks
import datetime
import pytz
from utils.configs import colors

UTC = pytz.utc


class Undawn(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.slash_command(name="setevent",
                          description="Set any scheduled event")
  @option("daily",
          description="True for everyday event",
          choices=["True", "False"])
  async def setevent_command(self,
                             ctx,
                             name: str,
                             time: str,
                             message=None,
                             image_url=None,
                             daily="False"):
    error = False
    error_message = "Please use time 24hr format ,Example 22:00 or 03:07 do not include any other symbol"

    def erEmb(error_message):
      return discord.Embed(title="Error!",
                           description=error_message,
                           color=colors['RED'])

    for item in time.replace(":", ""):
      if item.isnumeric():
        pass
      else:
        error = True
    if ":" not in list(time):
      return await ctx.respond(error_message)
    splitTime = time.split(":")
    if int(splitTime[0]) > 24 or int(splitTime[1]) > 60:
      error = True
    if image_url != None:
      if str(image_url).startswith("https://") or str(image_url).startswith(
          "http://"):
        pass
      else:
        error = True
        error_message = "Image url must be link!"
    if error:
      return await ctx.respond(embed=erEmb(error_message))
    sql = self.bot.db.execute(
      "insert into events (name,time,message,url,daily) values (?,?,?,?,?)",
      (name, time, message, image_url, daily))
    self.bot.conn.commit()
    embed = discord.Embed(
      title="Check for correction",
      description=
      f"Name : {name}\nTime : {time}\nMessage : {message}\nDaily : {daily}\nImage Link : {image_url}"
    )
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_footer(text=f"Requested by {ctx.author.name}",
                     icon_url=ctx.author.avatar)
    await ctx.respond(embed=embed)

  @commands.slash_command(name="delevent", description="Delete event")
  async def delevent(self, ctx, event_id: int):
    sql = self.bot.db.execute("delete from events where id = ?", (event_id, ))
    await ctx.respond(f"{ctx.author.mention} event deleted succesfully")

  @commands.slash_command(name="events",
                          description="Get list of scheduled events")
  async def events(self, ctx):
    evts = self.bot.db.execute("select * from events").fetchall()
    embed = discord.Embed(title="Scheduled Events", description="")
    for event in evts:
      timelist = event[2].split(":")
      eTimeLeftMin = int(event[0]) * 60 + int(timelist[1])
      timeLeftINMin = int(timelist[0]) * 60 + int(timelist[1])
      embed.add_field(
        name=event[1],
        value=
        f"**ID**: `{event[0]}`   **Daily Event**: {event[5]}\n**Time**: {event[2]}   **Time Left**: {timeLeftINMin}m"
      )
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
    embed.set_footer(text=f"Requested by {ctx.author.name}",
                     icon_url=ctx.author.avatar)
    await ctx.respond(embed=embed)

  @tasks.loop(seconds=60)
  async def send_event(self):
    channel = self.bot.get_channel(1162103853643202570)
    evts = self.bot.db.execute("select * from events").fetchall()
    time_india = pytz.timezone('Asia/Kolkata')
    utc_time = datetime.datetime.now(time_india)
    time = utc_time.strftime("%H:%M").split(":")
    timeInMin = int(time[0]) * 60 + int(time[1])
    for event in evts:
      eTime = event[2].split(":")
      eTimeInMin = int(eTime[0]) * 60 + int(eTime[1])
      name = event[1]
      message = event[3]
      url = event[4]
      if int(timeInMin) == int(eTimeInMin) - 10:
        embed = discord.Embed(title="Event Announcement!",
                              description=f"**{name}** will start in `10m`",
                              color=colors['RED'])
        if url:
          embed.set_image(url=url)
        if message:
          embed.add_field(name="Message", value=message)
        embed.timestamp = datetime.datetime.utcnow()
        await channel.send("@everyone", embed=embed)
      if int(timeInMin) == int(eTimeInMin):
        embed = discord.Embed(title="Event Announcement!",
                              description=f"**{name}** has started")
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar)
        embed.timestamp = datetime.datetime.utcnow()
        await channel.send(embed=embed)

  @send_event.before_loop
  async def before_event(self):
    print("Waiting for bot to be ready...")
    await self.bot.wait_until_ready()
    print("Bot is ready, starting the task.")


def setup(bot):
  cog = Undawn(bot)
  cog.send_event.start()
  bot.add_cog(cog)
