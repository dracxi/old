import discord
import random
from discord.ext import commands
from discord.commands import slash_command
from utils.HelpCommand import HelpEmbed
from ui.HelpUi import HelpView
import datetime
from utils.configs import colors

ball_responses = ['Yes', 'No', 'Try Again']
guild = 1031033900547448862


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.helpemb = HelpEmbed(bot)
        self.start_time = datetime.datetime.utcnow()

    @commands.slash_command(name='help',
                            description='Miko bot help command!!',
                            aliases=['commands', 'command'],
                            usage='cog')
    async def help_command(self, ctx, query='all'):
        if query == 'all':
            embed = await self.helpemb.HelpMain()
            await ctx.respond(embed= embed,view = HelpView(self.bot,timeout=30))
            return
        elif query in self.bot.cogs:
            embed = await self.helpemb.Help_cog(query)
            await ctx.respond(embed=embed,view = HelpView(self.bot,timeout=30))
        else:
            embed = await self.helpemb.Help_command(query)
            print(embed)
            await ctx.respond(embed=embed , view = HelpView(self.bot,timeout=30))
    @commands.command(name="status",description="Bot status")
    async def status(self, ctx):
        # Get latency/ping
        latency = self.bot.latency * 1000
        ping = f'{latency:.2f}ms'

        # Get server information
        server_count = len(self.bot.guilds)
        member_count = len(set(self.bot.get_all_members()))

        # Get uptime
        uptime_delta = datetime.datetime.utcnow() - self.start_time
        uptime_hours = int(uptime_delta.total_seconds() / 3600)
        uptime_minutes = int((uptime_delta.total_seconds() % 3600) / 60)
        uptime_seconds = int(uptime_delta.total_seconds() % 60)
        uptime = f'{uptime_hours}h {uptime_minutes}m {uptime_seconds}s'

        # Create embed
        embed = discord.Embed(title='Bot Status', color=discord.Color.green())
        embed.add_field(name='Bot Name', value=self.bot.user.name, inline=True)
        embed.add_field(name='Ping', value=ping, inline=True)
        embed.add_field(name='Server Count', value=server_count, inline=True)
        embed.add_field(name='Member Count', value=member_count, inline=True)
        embed.add_field(name='Uptime', value=uptime, inline=True)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.bot:
            return
        if message.content.lower().startswith("loc"):
            msg = str(message.content)[3:].split()
            help = HelpEmbed(self.bot)
            if msg[0].lower() =='help':
                if len(msg) == 2:
                    print(len(msg[1]),msg[1])
                    if msg[1] in self.bot.cogs:
                        print(1)
                        embed = await self.helpemb.Help_cog(msg[1])
                        await message.reply(embed = embed,view = HelpView(self.bot,timeout=30))
                    else:
                        print(2)
                        embed = await self.helpemb.Help_command(msg[1])
                        await message.reply(embed=embed , view = HelpView(self.bot,timeout=30))
                else:
                    print(3)
                    embed = await help.HelpMain()
                    await message.reply(embed=embed , view = HelpView(self.bot,timeout=30))
    async def on_command_error(self,ctx,error):
        if isinstance(error,commands.MissingPermissions):
            await ctx.respond(f"{error}")
        if isinstance(error, commands.NSFWChannelRequired):
            await ctx.respond(
                f"{ctx.author.mention} Use it on nsfw channel hornyass")

                
   
def setup(bot):
    bot.add_cog(General(bot))
