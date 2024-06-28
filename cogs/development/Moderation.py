import subprocess
import discord
import asyncio
from discord.ext import commands
from discord.commands import slash_command

guild = 1031033900547448862


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='ban', guild_ids=[guild])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if reason == None:
            reason = "no reason provided"
        await ctx.respond(
            f'User {member.mention} has been banned for "{reason}"')
        await ctx.guild.ban(member)

    # Kick Command
    @commands.slash_command(name='kick', guild_ids=[guild])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if reason == None:
            reason = "no reason provided"
        await ctx.respond(
            f'User {member.mention} has been kicked for "{reason}"')
        await ctx.guild.kick(member)

    @commands.slash_command(name="purge")
    @commands.has_permissions(administrator=True)
    async def _purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount)
        await ctx.respond(f'Deleted {amount} messages')

    @commands.slash_command(name='clear_dm', hidden=True)
    async def _cleardm(self, ctx, user: discord.Member, amount: int):
        async for message in self.bot.get_user(user.id).history(limit=amount):
            if ctx.author.id == user.id:
                await message.delete()
                await asyncio.sleep(0.5)


def setup(bot):
    bot.add_cog(Moderation(bot))
