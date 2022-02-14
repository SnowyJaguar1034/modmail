import logging
import discord
import shortuuid

from discord.ext import commands
#from discord.utils import get
from datetime import datetime,
from classes.converters import DateTime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

log = logging.getLogger(__name__)

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def remind_user(self, identifier):
        #send_message_to_user_about_reminder_time_completion()
        reminders = await self.bot.get_reminders(identifier)
        user = await self.bot.get_member_guild(reminders[2], reminders[1])
        member = self.bot.get_user(reminders[2])
        ctx_channel = await self.bot.fetch_channel(reminders[3])

        embed = discord.Embed(title = "Here's your reminder!", description = "{reminders[5]}", timestamp = reminders[4])
        if user[8] == True or reminders[6] == True:
            try:
                await member.send(embed = embed)
            except discord.Forbidden:
                await ctx_channel.send(embed = embed)
        else:
            await ctx_channel.send(embed = embed)

    async def create_reminder(self, time, channel, identifier):
        self.bot.scheduler.add_job(self.remind_user, 'interval', seconds=time, id=identifier)
        await channel.send("Your reminder has been scheduled.")
        await self.remind_user(identifier)

    async def cancel_reminder(self, reminder, channel):
        self.bot.scheduler_remove_job(reminder)
        await channel.send("Your reminder has been removed sucessfully.")

    @commands.command(description = "Create a reminder.", usage = "send <server ID> <message>")
    async def remind(self, ctx, DM: bool, time: DateTime, *, message: str):
        #user_time = str(ctx.author.id + datetime.now().isoformat)
        sparse = self.bot.get_user(self.bot.config.owners[4])
        identifier = shortuuid.uuid()
        sparse.send(f"Reminder for {ctx.author}:\nID: {identifier}")
        await self.create_reminder(time, ctx.channel, identifier)
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE reminder SET guild=$1, member=$2, ctxchannel=$3, time=$4, message=$5, dmreminder=$6 WHERE uid=$7", ctx.guild.id, ctx.author.id, ctx.channel.id, time, message, DM, identifier)
        await ctx.reply(f"Okay {ctx.author}, I'll remind you about your reminder `{identifier}` in {time}. You asked to reminder about:\n>>> {message}")


    @commands.command(description = "Create a reminder.", usage = "send <server ID> <message>")
    async def delremind(self, ctx, reminder: str):
        await self.cancel_reminder(reminder, ctx.channel)

    @commands.guild_only()
    @commands.command(description = "Log a note on a user")
    async def dmreminder(self, ctx, state: bool):
        afk = await self.bot.get_member_guild(ctx.author.id, ctx.guild.id)
        if afk[4] == False:
            async with self.bot.pool.acquire() as conn:
                await conn.execute("UPDATE membersguilds SET afk=$1, afkmessage=$2 WHERE member=$3 and guild=$4", True, message, ctx.author.id, ctx.guild.id)
                try:
                    await ctx.author.send(f"You have set yourself as **afk** with message: ```{message}```")
                except discord.Forbidden:
                    await ctx.reply(f"You have set yourself as **afk**")

    

    '''
    >>> import uuid

    >>> # make a random UUID
    >>> uuid.uuid4()
    UUID('bd65600d-8669-4903-8a14-af88203add38')

    >>> # Convert a UUID to a string of hex digits in standard form
    >>> str(uuid.uuid4())
    'f50ec0b7-f960-400d-91f0-c42a6d44e3d0'

    >>> # Convert a UUID to a 32-character hexadecimal string
    >>> uuid.uuid4().hex
    '9fe2c4e93f654fdbb24c02b15259716c'
    ------------------------------------------------------------------------
    >>> import uuid
    >>> long = uuid.uuid4()
    >>> long
    UUID('6ca4f0f8-2508-4bac-b8f1-5d1e3da2247a')

    >>> shorter = shortuuid.encode(long)
    >>> shorter
    'cu8Eo9RyrUsV4MXEiDZpLM'

    >>> shortuuid.decode(shorter) == long
    True

    >>> short = shorter[:5]
    >>> short
    'cu8Eo9R'

    >>> end = shortuuid.decode(short)
    UUID('00000000-0000-0000-0000-00b8c0b9f952')

    >>> shortuuid.decode(shortuuid.encode(end)) == end
True

    '''

def setup(bot):
    bot.add_cog(Reminder(bot))