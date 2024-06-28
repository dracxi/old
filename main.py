import discord
from discord.ext import commands
import sqlite3
import os
import subprocess
import shlex
import asyncio
from utils.HelpCommand import HelpEmbed
from ui.HelpUi import HelpView
from utils.configs import colors
import keep_alive

conn = sqlite3.connect("zervo.db")

db = conn.cursor()

db.execute("""
    create table IF NOT EXISTS users(
    dId INT PRIMARY KEY,
    zid INT NOT NULL,
    username TEXT NOT NULL,
    pUrl TEXT,
    desc TEXT,
    mCount INT
    )
    """)
conn.commit()

db.execute("""
    create table IF NOT EXISTS reactions(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    dId INT NOT NULL,
    keyword TEXT,
    desc TEXT,
    link TEXT,
    if_mention TEXT,
    if_None TEXT
    )
    """)
conn.commit()

db.execute("""
    create table IF NOT EXISTS globalchat(
    dId INT NOT NULL,
    gId INT NOT NULL,
    cId INT NOT NULL,
    active INT NOT NULL,
    cName TEXT
    )
    """)
conn.commit()

db.execute("""
    create table IF NOT EXISTS events(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    time TEXT NOT NULL,
    message TEXT,
    url TEXT,
    daily TEXT
    )
    """)
conn.commit()


class MyHelp(commands.HelpCommand):

    async def send_bot_help(self, mapping):
        if isinstance(mapping, set):
            mapping = {cog: cog.get_commands() for cog in mapping}
        channel = self.get_destination()
        help_embed = await helpembed.HelpMain()
        await channel.send(embed=help_embed, view=HelpView(bot))

    async def send_cog_help(self, cog):
        cog = cog.__cog_name__
        embed = await helpembed.Help_cog(cog)
        await self.get_destination().send(embed=embed,
                                          view=HelpView(bot),
                                          timeout=30)

    async def send_command_help(self, command):
        command = command.name
        embed = await helpembed.Help_command(command)
        await self.get_destination().send(embed=embed,
                                          view=HelpView(bot),
                                          timeout=30)

    async def send_error_message(self, error):
        command = error.replace('No command called "',
                                '').replace('" found.', "")
        embed = await helpembed.Help_command(command)
        await self.get_destination().send(embed=embed,
                                          view=HelpView(bot),
                                          timeout=30)


bot = commands.Bot(command_prefix='!',
                   intents=discord.Intents.all(),
                   help_command=MyHelp(),
                   activity=discord.Activity(
                       type=discord.ActivityType.listening, name='!help'))
cogs = ['cogs.General', 'cogs.Fun', 'cogs.Interactions', "cogs.Undawn"]
for cog in cogs:
    bot.load_extension(cog)

helpembed = HelpEmbed(bot)


@bot.event
async def on_ready():
    print("About the bot:")
    print(f"Username: {bot.user.name}")
    print(f"Bot ID: {bot.user.id}")
    bot.conn = conn
    bot.db = db
    bot.gc = db.execute("select * from globalchat")


@bot.command(name="addrole")
async def add_role(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send("added role")


@bot.command()
async def py(ctx, *, command: str):
    if ctx.author.id != 632748789341618207:
        await ctx.send("only drax can use this")
        return
    try:
        output = subprocess.check_output(['python3', '-c', f'{command}'],
                                         stderr=subprocess.STDOUT,
                                         text=True)
        # output = subprocess.check_output(command + ' 2>&1', shell=True, text=True)
        embed = discord.Embed(description=output,
                              color=colors['DARK_BUT_NOT_BLACK'])
        await ctx.send(embed=embed)
    except subprocess.CalledProcessError as e:
        embed = discord.Embed(title="ERROR",
                              description=f"{e.returncode}\n{e.output}")
        await ctx.send(embed=embed)
    except Exception as ex:
        await ctx.send(f'Error: {ex}')


@bot.command()
async def bash(ctx, *, command: str):
    if ctx.author.id != 632748789341618207:
        await ctx.send("only drax can use this")
        return
    try:
        # output = subprocess.check_output(['python3', '-c', f'{command}'],stderr=subprocess.STDOUT,text=True)
        output = subprocess.check_output(
            command + ' 2>&1', shell=True, text=True)
        embed = discord.Embed(description=output,
                              color=colors['DARK_BUT_NOT_BLACK'])
        await ctx.send(embed=embed)
    except subprocess.CalledProcessError as e:
        embed = discord.Embed(title="ERROR",
                              description=f"{e.returncode}\n{e.output}")
        await ctx.send(embed=embed)
    except Exception as ex:
        await ctx.send(f'Error: {ex}')


@bot.command()
async def sh(ctx, *, command: str):
    if ctx.author.id != 632748789341618207:
        await ctx.send("only drax can use this")
        return
    try:
        args = shlex.split(command)
        if args[0] == 'cd':
            os.chdir(args[1])
            output = f"Changed directory to: {args[1]}"
            embed = discord.Embed(description=output)
            await ctx.send(embed=embed)

        else:
            process = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            stdout = stdout.decode()
            stderr = stderr.decode()
            embed = discord.Embed(description=f"**Output**:\n{stdout}",
                                  color=colors['DARK_BUT_NOT_BLACK'])
            embed.set_footer(text=stderr)
            await ctx.send(embed=embed)

    except Exception as ex:
        await ctx.send(f'Error: {ex}')


@bot.command()
async def sql(ctx, *, command: str):
    if ctx.author.id != 632748789341618207:
        await ctx.send("Only authorized users can use this command.")
        return
    try:
        db.execute(command)
        result = db.fetchall()
        conn.commit()
        embed = discord.Embed(description=result,
                              color=colors['DARK_BUT_NOT_BLACK'])
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {e}")


keep_alive.keep_alive()
bot.run(os.environ.get('TOKEN'))
