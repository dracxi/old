from time import sleep
from dotenv import load_dotenv
import discord
import asyncio
import random
import requests
from discord.ext import commands
from discord import option
from discord.commands import slash_command
import datetime
import shutil
import aiohttp
import os

date = datetime.date.today()
year = date.year
load_dotenv()
hosturl = "https://wg6.pinpon.cool"


def calcd(udata):
    if udata['sex'] == 0:
        sex = 'Alien'
    elif udata['sex'] == 1:
        sex = 'Male'
    elif udata['sex'] == 2:
        sex = 'Female'
    uage = udata['birthday']
    byear = int(uage[0:4])
    bday = (uage[0:10])
    age = year - byear
    data = [bday, age, sex]
    return data


headers = {
    'accept-encoding': 'gzip',
    'app': 'zervo',
    'app-version': '168',
    'content-type': 'application/x-www-form-urlencoded',
    'host': 'wg6.pinpon.cool',
    'language': 'en_US',
    'platform': '0',
    'user-agent': 'Dart/3.1 (dart:io)'
}


async def login():
    global headers
    data = {
        "email": os.environ.get("email"),
        "password": os.environ.get("password"),
    }
    headers['content-type'] = "application/x-www-form-urlencoded;charset=utf-8"
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(f"{hosturl}/pinpon-app-auth/v3/auth/login/email",
                                data=data) as response:
            json_response = await response.json()
            if response.status == 200:
                auth_token = json_response["data"]["pinponToken"]["token"]
                headers["pinpon-auth"] = auth_token
                user_id = json_response['data']['appUserId']
                user_name = json_response['data']['id']
                print(f"logged in as {user_name}: {user_id}")
            else:
                print("Failed to login.")


async def get_profile(username):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(
                f"{hosturl}/pinpon-app-system/app-user/detail/{username}") as response:
            json_response = await response.json()
            return json_response


async def user_search(username):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(
            f"{hosturl}/pinpon-app-system/v5/app-recommend/all/search?current=1&name={username}&size=5"
        ) as response:
            json_response = await response.json()
            return json_response


async def world_info(id):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(
                f"{hosturl}/pinpon-app-system/app-plane/planeId/{id}") as response:
            json_response = await response.json()
            return json_response


async def get_oc(id: int):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(
            f'{hosturl}/pinpon-app-system/app-oc-count?appUserId={id}'
        ) as response:
            json_response = await response.json()
            return json_response


async def pfp(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{hosturl}/media/resize?inputFilename={url}&outputFilename=upload{url}&stretch=true&scale=0.6"
        ) as response:
            if response.status == 200:
                with open(url, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024):
                        f.write(chunk)
                return 'done'


class Zervo(commands.Cog, description="Zervo commands"):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="link", description="Link your zervo account")
    async def _link(self, ctx, username):
        c = self.bot
        desc = 'text'
        count = 1
        user = c.db.execute(f'select * from users where dId =?',
                            (ctx.author.id, )).fetchone()
        print(user)
        if user != None:
            await ctx.respond("You are already registered")
            return
        response = await get_profile(username)
        print(response)
        if response['code'] == 200:
            user = response['data']
            c.db.execute(
                "insert into users values(?,?,?,?,'Null',1)",
                (ctx.author.id, user['appUserId'], username, str(ctx.author.avatar)))
            c.conn.commit()
            await ctx.respond(
                "You are succesfully registerd use `/profile` to see you profile\n`/profile [discord user]` to see others profile"
            )
        else:
            embed = discord.Embed(
                title=f"[{username}] username not found",
                description='Make sure you are typing your unsername not nickname\nExample in this image\n**DraXy** is nickname and **@iloveyou2alien** is username\n```/register username:[Zervo username]``` without **@**'
            )
            embed.set_image(
                url='https://media.discordapp.net/attachments/1031232249858899988/1086128837886234754/Screenshot_20230317-085135_Zervo.png'
            )
            await ctx.respond(embed=embed)

    @commands.slash_command(name="usersearch", description='Get Zervo user info')
    async def _usersearch(self, ctx, username):
        response = await get_profile(username)

        if response['code'] != 200:
            response = await user_search(username)
            data = response['data']['appUserRecommendVOS']
            embed = discord.Embed(description=f"Search result for {username}")
            for dat in data:
                embed.add_field(
                    name=dat['nickname'],
                    value=f"**Username** : {dat['id']}\n**ID** : {dat['appUserId']}")

            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text=f"Requested by {ctx.author.name}",
                             icon_url=ctx.author.avatar)
            await ctx.respond(embed=embed)
            return

        udata = response['data']
        x = await asyncio.gather(get_oc(udata['appUserId']), pfp(udata['url']))
        data = calcd(udata)
        oc = x[0]['data']
        total_oc = oc['buyCount'] + 2
        print(oc)
        r = x[1]
        file = discord.File(udata["url"])
        embed = discord.Embed(
            title=udata['nickname'],
            url=f"https://www.zervo.me/people/{udata['appUserId']}",
            description=udata['bio'],
            color=0x36383e)
        embed.set_thumbnail(url=f"attachment://{file.filename}")
        embed.add_field(name="Username", value=udata['id'], inline=False)
        embed.add_field(name='UserId', value=udata['appUserId'], inline=False)
        embed.add_field(name='Points', value=udata['point'], inline=False)
        embed.add_field(name='BirthDay', value=data[0], inline=False)

        embed.add_field(name='Join Date',
                        value=udata['createTime'], inline=False)
        embed.add_field(name='OC count', value=total_oc, inline=True)
        embed.add_field(name='Age', value=data[1], inline=True)
        embed.add_field(name='Sex', value=data[2], inline=True)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"Requested by {ctx.author.name}",
                         icon_url=ctx.author.avatar)
        await ctx.respond(embed=embed, file=file)

    @commands.slash_command(name="profile", description="Get user zervo profile")
    async def _profile(self, ctx, member: discord.Member = None):
        c = self.bot
        if member == None:
            member = ctx.author
        user = c.db.execute("select * from users where dId =?",
                            (member.id, )).fetchone()
        if user == None:
            await ctx.respond("You are not registered")
        else:
            response = await get_profile(user[2])
            if response['code'] != 200:
                await ctx.respond("Something went wrong")
                return
        udata = response['data']
        x = await asyncio.gather(get_oc(udata['appUserId']), pfp(udata['url']))
        data = calcd(udata)
        oc = x[0]['data']
        total_oc = oc['buyCount'] + 2
        r = x[1]
        file = discord.File(udata["url"])
        embed = discord.Embed(
            title=udata['nickname'],
            url=f"https://www.zervo.me/people/{udata['appUserId']}",
            description=udata['bio'],
            color=0x36383e)
        embed.set_thumbnail(url=f"attachment://{file.filename}")
        embed.add_field(name="Username", value=udata['id'], inline=False)
        embed.add_field(name='UserId', value=udata['appUserId'], inline=False)
        embed.add_field(name='Points', value=udata['point'], inline=False)
        embed.add_field(name='BirthDay', value=data[0], inline=False)

        embed.add_field(
            name='Account Creation Date',
            value=f"**Zervo** : {udata['createTime']}\n**Discord** : {member.created_at.date()}",
            inline=False)
        embed.add_field(name='OC count', value=total_oc, inline=True)
        embed.add_field(name='Age', value=data[1], inline=True)
        embed.add_field(name='Sex', value=data[2], inline=True)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(
            text=f"Profile of {member.name}", icon_url=member.avatar)
        await ctx.respond(embed=embed, file=file)

    @commands.slash_command(name="unlink",
                            description="unlink your Zervo account")
    async def _unlink(self, ctx):
        c = self.bot
        user = c.db.execute("select * from users where dId =?",
                            (ctx.author.id, )).fetchone()
        if user[0] == None:
            await ctx.respond("you are not registed")
        c.db.execute("delete from users where dId = ?", (ctx.author.id, ))
        c.conn.commit()
        await ctx.respond("You are unlinked successfully")

    @commands.slash_command(
        name='world',
        description="Zervo world info",
    )
    async def _world(self, ctx, link: str):
        id = link.replace("https://www.zervo.me/world/", "")
        response = await world_info(id)
        data = response['data']
        if response['code'] == 200:
            await pfp(data["headUrl"])
            await pfp(data['backgroundUrl'])
            file = discord.File(data["headUrl"])
            file2 = discord.File(data['backgroundUrl'])
            embed = discord.Embed(title=data['name'],
                                  description=data['information'])
            # embed.set_thumbnail(url=f"attachment://{file.filename}")
            embed.add_field(name="World ID",
                            value=f"`{data['planeId']}`",
                            inline=True)
            embed.add_field(name="Language",
                            value=data["language"], inline=True)
            embed.add_field(name="Create time",
                            value=f"`{data['createTime']}`",
                            inline=True)
            embed.add_field(name="url", value=f"`{link}`")
            embed.set_image(url=f"attachment://{file2.filename}")
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text=f"Requested by {ctx.author.name}",
                             icon_url=ctx.author.avatar)
            await ctx.respond(embed=embed, file=file2)
        else:
            await ctx.respond("Please recheck the link")

    @commands.Cog.listener()
    async def on_ready(self):
        await login()


def setup(bot):
    bot.add_cog(Zervo(bot))
