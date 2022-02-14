import asyncio
import logging
import typing
import discord

from discord.ext import commands
from discord.utils import get
from utils import checks
from datetime import datetime, timedelta
from typing import Optional

log = logging.getLogger(__name__)

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Sets the age in days that a user has to meet to prevent them being kicked by raidmode.", alaises = ["jll", "joinlog", "leavelog"])
    async def joinleavelog(self, ctx, channel: discord.TextChannel = [], *, check = None):
        if check:
            await ctx.send(embed = discord.Embed(description = f"The channel is not found. Please try again.", colour = self.bot.error_colour,))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET joinleavelog=$1 WHERE guild=$2", channel.id, ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = f"The channel is updated successfully to {channel.mention}.", colour = self.bot.primary_colour))

    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Sets the log for deleted messages.", alaises = ["dml", "dellog", "deletelog"])
    async def deleted(self, ctx, channel: discord.TextChannel = [], *, check = None):
        if check:
            await ctx.send(embed = discord.Embed(description = f"The channel is not found. Please try again.", colour = self.bot.error_colour,))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET deletedmessages=$1 WHERE guild=$2", channel.id, ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = f"The channel is updated successfully to {channel.mention}.", colour = self.bot.primary_colour))

    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Sets the log for edited messages.", alaises = ["eml", "editlog"])
    async def edited(self, ctx, channel: discord.TextChannel = [], *, check = None):
        if check:
            await ctx.send(embed = discord.Embed(description = f"The channel is not found. Please try again.", colour = self.bot.error_colour,))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET editedmessages =$1 WHERE guild=$2", channel.id, ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = f"The channel is updated successfully to {channel.mention}.", colour = self.bot.primary_colour))

    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Sets the age in days that a user has to meet to prevent them being kicked by raidmode.", alaises = ["jll", "joinlog", "leavelog"])
    async def starboard(self, ctx, channel: discord.TextChannel = [], *, check = None):
        if check:
            await ctx.send(embed = discord.Embed(description = f"The channel is not found. Please try again.", colour = self.bot.error_colour,))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET starboard=$1 WHERE guild=$2", channel.id, ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = f"The channel is updated successfully to {channel.mention}.", colour = self.bot.primary_colour))

    @checks.in_database()
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Set or clear the channel to log raidmode messages.", usage = "raidmodelog <channel>", alaises = ["raidlog"], hidden = False)
    async def raidmodelog(self, ctx, channel: discord.TextChannel = [], *, check = None):
        if check:
            await ctx.send(embed = discord.Embed(description = f"The channel is not found. Please try again.", colour = self.bot.error_colour,))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET raidlog=$1 WHERE guild=$2", channel.id, ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = f"The channel is updated successfully to {channel.mention}.", colour = self.bot.primary_colour))
    
    @checks.in_database()
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Set or clear the channels to shutdown in a raid.", usage = "presetchannel <channel> [channels]", alaises = ["presetchan"], hidden = False)
    async def presetchannels(self, ctx, channels: commands.Greedy[discord.TextChannel] = [], *, check = None):
        if check:
            await ctx.send(embed = discord.Embed(description = f"The channel(s) are not found. Please try again.", colour = self.bot.error_colour,))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET raidchannel=$1 WHERE guild=$2", [channel.id for channel in channels], ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = "The channel(s) are updated successfully to".join(channels), colour = self.bot.primary_colour))

    @checks.in_database()
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Set or clear the roles to remove permissions from. If you have a Verification role, it must be the first role.", usage = "preset <role> [roles]", hidden = False)
    async def presetroles(self, ctx, roles: commands.Greedy[discord.Role] = [], *, check = None):
        if check:
            await ctx.send(embed = discord.Embed(description = f"The role(s) are not found. Please try again.", colour = self.bot.error_colour,))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET lockedroles=$1 WHERE guild=$2", [role.id for role in roles], ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = "The role(s) are updated successfully to".join(roles), colour = self.bot.primary_colour))

    @checks.in_database()
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Set or clear the counting channel.", usage = "countingchannel <channel>", alaises = ["countchan"], hidden = False)
    async def countingchannel(self, ctx, channel: discord.TextChannel, *, check = None):
        if check:
            await ctx.send(embed = discord.Embed(description = f"The channel is not found. Please try again.", colour = self.bot.error_colour,))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET countchannel=$1 WHERE guild=$2", channel.id, ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = "The channel is updated successfully to {channel.mention}.", colour = self.bot.primary_colour))

    @checks.in_database()
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Set or clear the roles that get assigned on a counting mistake.", aliases = ["failrole"], usage = "mistakesrole <role> [roles]")
    async def mistakesrole(self, ctx, roles: commands.Greedy[discord.Role] = None, *, check = None):
        if roles is None:
            roles = []
        if check:
            await ctx.send(embed = discord.Embed(description = "The role(s) are not found. Please try again.", colour = self.bot.error_colour))
            return
        if len(roles) > 10:
            await ctx.send(embed = discord.Embed(description = "There can at most be 10 roles. Try using the command again but specify less roles.", colour = self.bot.error_colour))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET mistakesrole=$1 WHERE guild=$2", [role.id for role in roles], ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = "The role(s) are updated successfully.", colour = self.bot.primary_colour))

    @checks.in_database()
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Set or clear the suggestions channel.", usage = "suggestionchannel <channel>", alaises = ["sugchan"], hidden = False)
    async def suggestionchannel(self, ctx, channel: discord.TextChannel, *, check = None):
        if check:
            await ctx.send(embed = discord.Embed(description = f"The channel is not found. Please try again.", colour = self.bot.error_colour,))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET suggestions=$1 WHERE guild=$2", channel.id, ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = f"The channel is updated successfully to {channel.mention}.", colour = self.bot.primary_colour))

def setup(bot):
    bot.add_cog(Logs(bot))