import asyncio
import logging
import discord
from discord.ext import commands
from discord.utils import get
from utils import checks

log = logging.getLogger(__name__)

class Miscellaneous(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.current_number = 0
        #self.guild_mistakes = 0
        self.member_mistakes = 0
        self.member_allowed = 3
        #self.mistakes_role = 725728679082328075

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            data = await self.bot.get_data(message.guild.id)
            mistakes = await self.bot.get_member_guild(message.author.id, message.guild.id)
            self.current_number = data[13]
            isolation_time = data[20]
            if message.author != self.bot.user:
                #assert message.channel.id in data[17]
                #for channel in data[17]:
                if message.channel.id == data[22]:
                    # message_content = message.content
                    number = message.content.split(' ')[0]
                    try:
                        number = int(number)
                    except:
                        return
                    if number < 1:
                        return
                    if number == data[13] + 1:
                        with message.channel.typing():
                            await message.add_reaction('✅')
                            self.current_number = number
                            async with self.bot.pool.acquire() as conn:
                                await conn.execute("UPDATE data SET currentcount=$1 WHERE guild=$2", self.current_number, message.guild.id,)
                    else:
                        self.current_number = data[13]
                        await message.add_reaction('❌')
                        mistakes_count = mistakes[3] + 1
                        #await message.channel.send(f'{message.author.name}#{message.author.discriminator} ruined the count at **{self.current_number + 1}**!! The next number is **1**.')
                        async with self.bot.pool.acquire() as conn:
                            await conn.execute("UPDATE data SET currentcount=$1 WHERE guild=$2", self.current_number, message.guild.id,)
                            await conn.execute("UPDATE membersguilds SET mistakes=$1 WHERE member=$2 and guild=$3", mistakes_count, message.author.id, message.guild.id)
                        if mistakes[3] > 3:
                            tmp = [] # some temp list to append the role objects in
                            for id in data[17]:
                                tmp.append(discord.Object(id))
                            await message.author.add_roles(*tmp, reason = f"{message.author} got the number wrong in {message.channel.name} and so has temporarily been given this role.", atomic = True)

    @commands.has_permissions(administrator = True)
    @commands.command(description = "Set the number to count from.", usage = "setcount", aliases = ["set-count"])
    async def setcount(self, ctx, setcount : int):
        temp = self.current_number
        self.current_number = setcount
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET currentcount=$1 WHERE guild=$2", self.current_number, ctx.guild.id,)
        await ctx.send(embed = discord.Embed(description = f"The number to count from has been changed from `{temp}` to `{setcount}`", colour = ctx.author.colour))

    @commands.command(description = "Show the current number in the count.", usage = "countingstats", aliases = ["countinfo", "count-stats", "count-info", "countingstats", "countinginfo", "counting-stats", "counting-info"])
    async def countstats(self, ctx):
        data = await self.bot.get_data(ctx.guild.id)
        counting_channel = ctx.guild.get_channel(data[22])
        mistakes_roles = []
        for role in data[17]:
            if role == -1:
                mistakes_roles.append("@here")
            elif role == ctx.guild.default_role.id:
                mistakes_roles.append("@everyone")
            else:
                mistakes_roles.append(f"<@&{role}>")

        embed = discord.Embed(title = "Counting Stats", colour = ctx.author.colour)
        embed.add_field(name = "Current Number", value = data[13], inline = True)
        embed.add_field(name = "Next Number", value = f"{data[13] + 1}", inline = True)
        embed.add_field(name="Counting Channel", value = "*Not set*" if counting_channel is None else f"<#{counting_channel.id}>", inline = True)
        embed.add_field(name = "Mistakes Roles", value = "*Not set*" if len(mistakes_roles) == 0 else " ".join(mistakes_roles), inline = False)
        await ctx.send(embed = embed)

    @commands.command(description = "Add yourself to the databse so that you can set reminders, a afk status's and more.", usage = "mg")
    async def mg(self, ctx):
        with ctx.channel.typing():
            count = 0
            async with self.bot.pool.acquire() as conn:
                await conn.execute("UPDATE membersguilds SET joincount=$1 WHERE member=$2 and guild=$3", count, ctx.author.id, ctx.guild.id)
            embed = discord.Embed(title = ctx.author, description = "You have been added to the database.")

    @commands.command(description = "Add a user to the databse. (`,mg`) alternativly.", usage = "mg_add <member>")
    async def mg_add(self, ctx,):
        with ctx.channel.typing():
            snowyjaguar = self.bot.get_user(self.bot.config.owner)
            for guild in self.bot.guilds:
                for member in guild.members:
                    
                    #yield member

                    #joincount = await self.bot.get_member_guild(member.id, guild.id)
                    #count = 0
                    async with self.bot.pool.acquire() as conn:
                        await conn.execute("UPDATE membersguilds SET g_name=$1 WHERE member=$2 and guild=$3", guild.name, member.id, guild.id)
                        await conn.execute("UPDATE membersguilds SET m_name=$1 WHERE member=$2 and guild=$3", member.name, member.id, guild.id)


                    await snowyjaguar.send(embed = discord.Embed(title = member, colour = ctx.author.colour, description = f"You have added `{member}` to the database for `{guild}`."))

def setup(bot: commands.Bot):
    bot.add_cog((Miscellaneous(bot)))