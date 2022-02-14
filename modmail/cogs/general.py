import logging
import platform
import time
import datetime
import discord
import psutil
import random
import discord_slash
import io

from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, cog_ext
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import ButtonStyle

from utils import checks
from utils.paginator import Paginator
from datetime import datetime
from config import default_prefix
from time import sleep

log = logging.getLogger(__name__)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        psutil.cpu_percent()
        self.suggestions = 0

    @commands.command(description = "🏓 Pong! Get my latency.", usage = "ping")
    async def ping(self, ctx):
        start = time.time()
        msg = await ctx.reply(embed = discord.Embed(description = "Checking latency...", colour = self.bot.primary_colour))
        sleep(1.5)
        await msg.edit(embed = discord.Embed(title = "🏓 Pong!", description = f"🚪 Gateway latency: {round(self.bot.latency * 1000, 2)}ms.\n📰 HTTP API latency: {round((time.time() - start) * 1000, 2)}ms.", colour = self.bot.primary_colour,))

    @cog_ext.cog_slash(name = "ping",)
    async def _ping(self, ctx: SlashContext):
        start = time.time()
        msg = await ctx.reply(embed = discord.Embed(description = "Checking latency...", colour = self.bot.primary_colour))
        sleep(1.5)
        await msg.edit(embed = discord.Embed(title = "🏓 Pong!", description = f"🚪 Gateway latency: {round(self.bot.latency * 1000, 2)}ms.\n📰 HTTP API latency: {round((time.time() - start) * 1000, 2)}ms.", colour = self.bot.primary_colour,))

    def get_bot_uptime(self, *, brief=False):
        hours, remainder = divmod(int(self.bot.uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if not brief:
            if days:
                fmt = "{d} days, {h} hours, {m} minutes, and {s} seconds"
            else:
                fmt = "{h} hours, {m} minutes, and {s} seconds"
        else:
            fmt = "{h}h {m}m {s}s"
            if days:
                fmt = "{d}d " + fmt
        return fmt.format(d = days, h = hours, m = minutes, s = seconds)

    @commands.command(description = "Check how long I've been online for", usage = "uptime", aliases = ["online", "alive"],)
    async def uptime(self, ctx):
        #embed = discord.Embed(colour = self.bot.primary_colour)
        #embed.add_field(name = "Uptime", value = self.get_bot_uptime(brief = True), inline = True)
        #embed.add_field(name = "Launched", value = self.bot.start_time.strftime("%d/%m/%Y %I:%M %p"), inline = True)
        await ctx.reply(f"I have been online for **{self.get_bot_uptime(brief = True)}** and was last started on **{self.bot.start_time.strftime('%A %d %B %Y')}** at **{self.bot.start_time.strftime('%I:%M %p')}**.")

    @cog_ext.cog_slash(name = "uptime", description = "Check how long I've been online for.",)
    async def _uptime(self, ctx: SlashContext):
        guilds = sum(await self.bot.comm.handler("guild_count", self.bot.cluster_count))
        await ctx.reply(f"I have been online for **{self.get_bot_uptime(brief = False)}** and was last started on **{self.bot.start_time.strftime('%A %d %B %Y')}** at **{self.bot.start_time.strftime('%I:%M %p')}**.")

    @commands.command(description = "See some super cool statistics about me.", usage = "stats", aliases = ["statistics"],)
    async def stats(self, ctx):
        guilds = sum(await self.bot.comm.handler("guild_count", self.bot.cluster_count))
        #channels = sum(await self.bot.comm.handler("channel_count", self.bot.cluster_count))
        #users = sum(await self.bot.comm.handler("user_count", self.bot.cluster_count))

        embed = discord.Embed(title = f"{self.bot.user.name} Statistics", description=  f"**Pong!** 🏓 My latency to this server is **{round(self.bot.latency * 1000)}**ms", colour = self.bot.primary_colour)
        embed.set_thumbnail(url = self.bot.user.avatar_url)
        embed.set_author(name = "Made with ❤ using discord.py", icon_url = "https://www.python.org/static/opengraph-icon-200x200.png",)
        embed.set_footer(text = f"Launched {self.bot.start_time.strftime('%d/%m/%Y %I:%M %p')} | {self.bot.start_time.strftime('%A %d %B %Y')} at {self.bot.start_time.strftime('%I:%M %p')}")

        #embed.add_field(name = "Developer", value = "CHamburr#2591")
        embed.add_field(name = "Owner", value = "SnowyJaguar#1034")
        embed.add_field(name = "Prefix Default/Server", value = f"`{default_prefix}`/`{ctx.prefix}`")
        embed.add_field(name = "Servers", value = str(guilds))
        embed.add_field(name = "Bot Version", value = self.bot.version)
        embed.add_field(name = "Python Version", value = platform.python_version())
        embed.add_field(name = "discord.py Version", value = discord.__version__)
        embed.add_field(name = " discord-interactions Version", value = discord_slash.__version__)
        embed.add_field(name = "CPU Usage", value = f"{psutil.cpu_percent(interval=None)}%")
        embed.add_field(name = "RAM Usage", value = f"{psutil.virtual_memory().percent}%")
        embed.add_field(name = "Emoji's accessible", value = len(self.bot.emojis))
        embed.add_field(name = "Uptime", value = self.get_bot_uptime(brief = True))
        embed.add_field(name="Clusters", value=f"{self.bot.cluster}/{self.bot.cluster_count}")
        if ctx.guild:
            embed.add_field(name="Shards", value=f"{ctx.guild.shard_id + 1}/{self.bot.shard_count}")
        else:
            embed.add_field(name="Shards", value=f"{self.bot.shard_count}")

        #embed.add_field(name = "Launched", value = f"{self.bot.start_time.strftime('%d/%m/%Y %I:%M %p')} | {self.bot.start_time.strftime('%A %d %B %Y')} at {self.bot.start_time.strftime('%I:%M %p')}", inline = True)
        #embed.add_field(name = "Channels", value = str(channels))
        #embed.add_field(name = "Users", value = str(users))
        await ctx.reply(embed = embed)

    @cog_ext.cog_slash(name = "stats", description = "See some super cool statistics about me.",)
    async def _stats(self, ctx: SlashContext):
        guilds = sum(await self.bot.comm.handler("guild_count", self.bot.cluster_count))

        embed = discord.Embed(title = f"{self.bot.user.name} Statistics", description=  f"**Pong!** 🏓 My latency to this server is **{round(self.bot.latency * 1000)}**ms", colour = self.bot.primary_colour)
        embed.set_thumbnail(url = self.bot.user.avatar_url)
        embed.set_author(name = "Made with ❤ using discord.py", icon_url = "https://www.python.org/static/opengraph-icon-200x200.png",)
        embed.set_footer(text = f"Launched {self.bot.start_time.strftime('%d/%m/%Y %I:%M %p')} | {self.bot.start_time.strftime('%A %d %B %Y')} at {self.bot.start_time.strftime('%I:%M %p')}")

        embed.add_field(name = "Owner", value = "SnowyJaguar#1034")
        embed.add_field(name = "Prefix", value = f"`{default_prefix}`")
        embed.add_field(name = "Servers", value = str(guilds))
        embed.add_field(name = "Bot Version", value = self.bot.version)
        embed.add_field(name = "Python Version", value = platform.python_version())
        embed.add_field(name = "discord.py Version", value = discord.__version__)
        embed.add_field(name = " discord-interactions Version", value = discord_slash.__version__)
        embed.add_field(name = "CPU Usage", value = f"{psutil.cpu_percent(interval=None)}%")
        embed.add_field(name = "RAM Usage", value = f"{psutil.virtual_memory().percent}%")
        embed.add_field(name = "Emoji's accessible", value = len(self.bot.emojis))
        embed.add_field(name = "Uptime", value = self.get_bot_uptime(brief = True))
        embed.add_field(name="Clusters", value=f"{self.bot.cluster}/{self.bot.cluster_count}")
        if ctx.guild:
            embed.add_field(name="Shards", value=f"{ctx.guild.shard_id + 1}/{self.bot.shard_count}")
        else:
            embed.add_field(name="Shards", value=f"{self.bot.shard_count}")
        await ctx.reply(embed = embed)

    @commands.command(description = "Get a link to invite me.", usage = "invite", hidden = True)
    async def invite(self, ctx):
        invite = await self.bot.comm.handler("invite_guild", -1, {"guild_id": ctx.guild.id})
        if not invite:
            await ctx.send(embed = discord.Embed(description = "No permissions to create an invite link.", colour = self.bot.primary_colour))
        else:
            buttons = [create_button(style = ButtonStyle.blue.URL, url = f"https://discord.gg/{invite.code}", label = f"Invite someone to {ctx.guild.name}")]
            action_row = create_actionrow(*buttons)

            await ctx.reply(content = f"You can invite people to this server by sharing this code: `https://discord.gg/{invite.code}`.", components = [action_row])
            button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
            await button_ctx.edit_origin(content = "You pressed a button!")

    @cog_ext.cog_slash(name = "invite", description = "Get a link to the server to invite other people.",)
    async def _invite(self, ctx: SlashContext):
        invite = await self.bot.comm.handler("invite_guild", -1, {"guild_id": ctx.guild.id})
        if not invite:
            await ctx.send(embed = discord.Embed(description = "No permissions to create an invite link.", colour = self.bot.primary_colour))
        else:
            buttons = [create_button(style = ButtonStyle.blue.URL, url = f"https://discord.gg/{invite.code}", label = f"Invite someone to {ctx.guild.name}")]
            action_row = create_actionrow(*buttons)

            await ctx.reply(content = f"You can invite people to this server by sharing this code: `https://discord.gg/{invite.code}`.", components = [action_row])
            button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
            await button_ctx.edit_origin(content = "You pressed a button!")

    @commands.command(description = "Join, or invite someone to, the crew.", usage = "invite", hidden = True)
    async def crew(self, ctx):
        buttons = [create_button(style = ButtonStyle.blue.URL, url = f"https://socialclub.rockstargames.com/crew/gofs_crew/wall", label = f"{ctx.guild.name} crew page")]
        action_row = create_actionrow(*buttons)

        await ctx.reply(content = f"You can invite people to {ctx.guild.name} crew by sending them this link: `https://socialclub.rockstargames.com/crew/gofs_crew/wall`.", components = [action_row])
        button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
        await button_ctx.edit_origin(content = "You pressed a button!")

    @cog_ext.cog_slash(name = "crew", description = "Join, or invite someone to, the crew.",)
    async def _crew(self, ctx: SlashContext):
        buttons = [create_button(style = ButtonStyle.blue.URL, url = f"https://socialclub.rockstargames.com/crew/gofs_crew/wall", label = f"{ctx.guild.name} crew page")]
        action_row = create_actionrow(*buttons)

        await ctx.reply(content = f"You can invite people to {ctx.guild.name} crew by sending them this link: `https://socialclub.rockstargames.com/crew/gofs_crew/wall`.", components = [action_row])
        button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
        await button_ctx.edit_origin(content = "You pressed a button!")

    @commands.command(description = "Join, or invite someone to, the crew.", usage = "invite", hidden = True)
    async def club(self, ctx):
        buttons = [create_button(style = ButtonStyle.blue.URL, url = f"https://account.xbox.com/en-gb/clubs/profile?clubid=3379881540920599", label = f"{ctx.guild.name} XBox Club")]
        action_row = create_actionrow(*buttons)

        await ctx.reply(content = f"You can send people to {ctx.guild.name} XBox Club by sending them this link: `https://account.xbox.com/en-gb/clubs/profile?clubid=3379881540920599`.", components = [action_row])
        button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
        await button_ctx.edit_origin(content = "You pressed a button!")

    @cog_ext.cog_slash(name = "club", description = "Join, or invite someone to, the crew.",)
    async def _club(self, ctx: SlashContext):
        buttons = [create_button(style = ButtonStyle.blue.URL, url = f"https://account.xbox.com/en-gb/clubs/profile?clubid=3379881540920599", label = f"{ctx.guild.name} XBox Club")]
        action_row = create_actionrow(*buttons)

        await ctx.reply(content = f"You can send people to {ctx.guild.name} XBox Club by sending them this link: `https://account.xbox.com/en-gb/clubs/profile?clubid=3379881540920599`.", components = [action_row])
        button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
        await button_ctx.edit_origin(content = "You pressed a button!")

    @commands.command(description = "Link to the GOFS subreddit.")
    async def reddit(self, ctx):
        buttons = [create_button(style = ButtonStyle.blue.URL, url = f"https://reddit.com/r/GOFS_Crew/?utm_medium=android_app&utm_source=share", label = f"{ctx.guild.name} crew page")]
        action_row = create_actionrow(*buttons)

        await ctx.reply(content = f"You can invite people to {ctx.guild.name} reddit by sending them this link: `https://reddit.com/r/GOFS_Crew/?utm_medium=android_app&utm_source=share`.", components = [action_row])
        button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
        await button_ctx.edit_origin(content = "You pressed a button!")

    @cog_ext.cog_slash(name = "reddit", description = "Link to the GOFS subreddit",)
    async def _reddit(self, ctx: SlashContext):
        buttons = [create_button(style = ButtonStyle.blue.URL, url = f"https://reddit.com/r/GOFS_Crew/?utm_medium=android_app&utm_source=share", label = f"{ctx.guild.name} crew page")]
        action_row = create_actionrow(*buttons)

        await ctx.reply(content = f"You can invite people to {ctx.guild.name} reddit by sending them this link: `https://reddit.com/r/GOFS_Crew/?utm_medium=android_app&utm_source=share`.", components = [action_row])
        button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
        await button_ctx.edit_origin(content = "You pressed a button!")

    @commands.command(description = "See how many servers I'm in.", usage = "servers")
    async def servers(self, ctx):
        guilds = sum(await self.bot.comm.handler("guild_count", self.bot.cluster_count))
        await ctx.reply(f"I am in {str(guilds)} servers! Their names are: {', '.join([guild.name for guild in self.bot.guilds])}" )

    @cog_ext.cog_slash(name = "servers", description = "See how many servers this bot is in as well nas their names.")
    async def _servers(self, ctx: SlashContext):
        await ctx.reply(f"I am in {str(len(self.bot.guilds))} servers! Their names are: {', '.join([guild.name for guild in self.bot.guilds])}")

    
    #def get_human_readable_size(self, num):
        #exp_str = [ (0, 'B'), (10, 'KB'),(20, 'MB'),(30, 'GB'),(40, 'TB'), (50, 'PB'),]               
        #i = 0
        #while i + 1 < len(exp_str) and num >= (2 ** exp_str[i+1][0]):
            #i += 1
            #rounded_val = round(float(num) / 2 ** exp_str[i][0], 2)
        #return '%s %s' % (int(rounded_val), exp_str[i][1])
    #total_size = get_human_readable_size(psutil.virtual_memory().total)

    @commands.command(description = "See my hardware information.", usage = "taskmanager", aliases = ["task-manager", "usage", "cpu", "ram"])
    async def taskmanager(self, ctx):
        embed = discord.Embed(colour = ctx.author.colour)
        #embed.add_field(name = "Number of CPU's", value = f"{psutil.cpu_count(logical=True)}")
        embed.add_field(name = "CPU Usage", value = f"{psutil.cpu_percent(interval=None)}%")
        #embed.add_field(name = "Total RAM", value = f"{total_size}")
        embed.add_field(name = "RAM Usage", value = f"{psutil.virtual_memory().percent}%")
        await ctx.reply(embed = embed)

    @cog_ext.cog_slash(name = "taskmanager", description = "See my hardware information.",)
    async def _taskmanager(self, ctx: SlashContext):
        embed = discord.Embed(colour = ctx.author.colour)
        embed.add_field(name = "CPU Usage", value = f"{psutil.cpu_percent(interval=None)}%")
        embed.add_field(name = "RAM Usage", value = f"{psutil.virtual_memory().percent}%")
        await ctx.reply(embed = embed)

    @commands.command(description = "See what versions of my libraries/lanaguge I am running.", usage = "versions", aliases = ["python", "discord.py"])
    async def versions(self, ctx):
        embed = discord.Embed(colour = ctx.author.colour)
        embed.add_field(name = "Bot Version", value = self.bot.version)
        embed.add_field(name = "Python Version", value = platform.python_version())
        embed.add_field(name = "discord.py Version", value = discord.__version__)
        await ctx.reply(embed = embed)

    @cog_ext.cog_slash(name = "versions", description = "See what versions of my libraries/lanaguge I am running..",)
    async def _versions(self, ctx: SlashContext):
        embed = discord.Embed(colour = ctx.author.colour)
        embed.add_field(name = "Bot Version", value = self.bot.version)
        embed.add_field(name = "Python Version", value = platform.python_version())
        embed.add_field(name = "discord.py Version", value = discord.__version__)
        await ctx.reply(embed = embed)

    @commands.command(description = "Lets users quote messages.", usage = "quote <messsage link or message ID>", aliases = ["q"])
    async def quote(self, ctx, message: discord.Message):
        plain = f"Sent <t:{int(message.created_at.timestamp())}:R> by {message.author} in {message.channel.mention}\n\n>>> {message.content}"
        buttons = [create_button(style = ButtonStyle.blue.URL, url = message.jump_url, label = f"Jump to message")]
        action_row = create_actionrow(*buttons)
        await ctx.reply(content = plain, embed = message.embeds[0].copy(), components = [action_row])
        if len(message.embeds) > 0:
            await ctx.reply(content = plain, embed = message.embeds[0].copy(), components = [action_row])
            for embed in message.embeds[1:]:
                await ctx.reply(embed = embed.copy())
        else:
            await ctx.reply(content = plain, components = [action_row])
        if len(message.attachments):
                for attachment in message.attachments:
                    await ctx.reply(content = attachment)
        button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
        await button_ctx.edit_origin(content = "You pressed a button!")


    @commands.command(description = "Quick and easy yes/no poll", usage = "poll", aliases = ["basic-poll", "basicpoll"])
    async def poll(self, ctx, title : str, *, message : str):
        embed = discord.Embed(colour = ctx.author.colour, title = title, description = message)
        embed.set_author(name = f" Asked by {str(ctx.author)}", icon_url = ctx.author.avatar_url)
        embed.set_footer(text = "Use the below reactions to up/down vote the poll")
        msg = await ctx.reply(embed = embed)
        await msg.add_reaction("<a:thisbeautiful:791806355560071198>")
        await msg.add_reaction("<a:thatbeautiful:856546821149032488>")

    @commands.command(description = "Multiple choice poll", usage = "advancedpoll", aliases = ["advanced-poll", "apoll", "a-poll"])
    async def advancedpoll(self, ctx, title : str, *options : str):
        print(random.choice(self.bot.emojis))
        log.info(random.choice(self.bot.emojis))
        if len(options) > 20:
            embed = discord.Embed(colour = ctx.author.colour, title = "❌", description = "Too many options given. You can only have a maximum of 20 options.")
            await ctx.send(embed = embed)
        else:
            embed = discord.Embed(colour = ctx.author.colour, title = title)
            embed.set_author(name = f" Asked by {str(ctx.author)}", icon_url = ctx.author.avatar_url)
            embed.set_footer(text = "Use the below reactions to vote")
            msg = await ctx.reply(embed = embed)
            for option, emoji in zip(options, random.choice(self.bot.emojis)):
                await msg.edit(embed = embed.add_field(name = emoji, value = option, inline = True))
                await msg.add_reaction(emoji)

    @commands.command(description = "Send us a suggestion.", usage = "sug <Suggestion>", aliases = ["sug"])
    async def suggest(self, ctx, *, suggestion_mesage : str):
        data = await self.bot.get_data(ctx.guild.id)
        suggestion_log = ctx.guild.get_channel(data[25])
        files = []
        suggestion_post = discord.Embed(colour = ctx.author.colour, title = f"Suggestion", description = suggestion_mesage)
        post = await suggestion_log.send(embed = suggestion_post)
        suggestions = await self.bot.get_sug(post.id, ctx.guild.id)
        await post.add_reaction("<a:thisbeautiful:791806355560071198>")
        await post.add_reaction("<a:thatbeautiful:856546821149032488>")
        suggestion_post = discord.Embed(colour = ctx.author.colour, title = f"Suggestion {suggestions[5]}", description = suggestion_mesage)
        suggestion_post.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        suggestion_post.set_footer(text = "Use the below reactions to up/down vote the suggestion")
        if len(ctx.message.attachments): # Checking if the orignal message contained a image
            suggestion_post.set_image(url = ctx.message.attachments[0].url)
        await post.edit(embed = suggestion_post)
        for file in ctx.message.attachments:
            saved_file = io.BytesIO()
            await file.save(saved_file)
            files.append(discord.File(saved_file, file.filename))
        await ctx.author.send(content = f"Your suggestion has been logged in {suggestion_log.mention} as suggestion `#{suggestions[5]}`. Your suggest contained {len(ctx.message.attachments)} but only the first attachment was posted. Your suggestion was:\n {suggestion_mesage}", files = files)
        await ctx.message.delete()
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE suggestions SET member=$1, original=$2, message=$3 where post=$4 and guild=$5", ctx.author.id, ctx.message.id, suggestion_mesage, post.id, ctx.guild.id)
            await conn.execute("UPDATE data SET sugcount=$1 WHERE guild=$2", suggestions[5], ctx.guild.id,)

    #@cog_ext.cog_slash(name = "suggest", description = "See what versions of my libraries/lanaguge I am running..", options = [create_option(name = "suggestion", description = "Let us know your amazing ideas.", option_type = 3, required = True,)])
    #async def _suggest(self, ctx: SlashContext, *, suggestion_mesage: str):

        #reactions = ["<:GOFS:791807697187766292>", "<:twitter:852658019510124554>", "<:Vinewoodboulevardradio:791808927708610560>", "<:gofs:737048621144473704>", "<:gold:791806448932880384>", "<:XboxOneGreen:791805440941752360>", "<:Radiomirrorpark:791808879171600394>", "<:rockthonk:791806622607474740>", "<a:thinkloading:840330853484986428>", "<:gta5:837393419944067142>", "<:discord:796754811798028288>", "<:booster:861022873715343382>", "<:bomb:500637957204475906>", "<:grenade:675648409801326592>", "<a:cashfly:791812165736595487>", "<:tombstone:501137177468731447>", "<:jet:675648637631463444>", "<:TheLab:791808896259063838>", "<:Twitch:852658101895168002>", "<a:BabyYodaSip:816069062815121448>"]


    @commands.command(description = "Log a note on a user")
    async def note(self, ctx, member: discord.Member, *, note: str):
        notes = self.bot.get_channel(id = 816693375637913643)
        embed = discord.Embed(title = f"New note on {member}", description = note, colour = ctx.author.colour)
        embed.set_author(name = f"{member} | {member.id}",icon_url = member.avatar_url)
        embed.set_footer(text = f"{ctx.author}", icon_url = ctx.author.avatar_url)
        await notes.send(embed = embed)
        await ctx.reply(f"Your note on {member.mention} has been logged in {notes.mention} <a:pepeNoted:936739396458270760>")

    @cog_ext.cog_slash(name = "note", description = "Log a note on a user", options = [
        create_option(
            name = "member", 
            description = "Member is required.", 
            option_type = 6, 
            required = True,
        ), 
        create_option(
            name = "note", 
            description = "Note is required..", 
            option_type = 3, 
            required = True,
        )
    ])
    async def _note(self, ctx: SlashContext, member: discord.Member, *, note: str):
        notes = self.bot.get_channel(id = 816693375637913643)
        embed = discord.Embed(title = f"New note on {member}", description = note, colour = ctx.author.colour)
        embed.set_author(name = f"{member} | {member.id}",icon_url = member.avatar_url)
        embed.set_footer(text = f"{ctx.author}", icon_url = ctx.author.avatar_url)
        await notes.send(embed = embed)
        await ctx.reply(f"Your note on {member.mention} has been logged in {notes.mention} <:pepeNoted:936739396458270760>")

    @cog_ext.cog_slash(name = "afk", description = "Set yourself as afk", options = [
        create_option(
            name = "message", 
            description = "Set a message that will be shown to people who ping you.", 
            option_type = 3, 
            required = False,
        ),
     ])
    async def _afk(self, ctx: SlashContext, *, message: str = None):
        afk = await self.bot.get_member_guild(ctx.author.id, ctx.guild.id)
        if afk[4] == False:
            async with self.bot.pool.acquire() as conn:
                await conn.execute("UPDATE membersguilds SET afk=$1, afkmessage=$2 WHERE member=$3 and guild=$4", True, message, ctx.author.id, ctx.guild.id)
            try:
                await ctx.author.send(f"You have set yourself as {f'**afk** with message: ```{message}```' if message is not None else '**afk**'}")
            except discord.Forbidden:
                await ctx.reply(f"You have set yourself as **afk**")

    @commands.guild_only()
    @commands.command(description = "Log a note on a user")
    async def afk(self, ctx, *, message: str = "No message provided"):
        afk = await self.bot.get_member_guild(ctx.author.id, ctx.guild.id)
        if afk[4] == False:
            async with self.bot.pool.acquire() as conn:
                await conn.execute("UPDATE membersguilds SET afk=$1, afkmessage=$2 WHERE member=$3 and guild=$4", True, message, ctx.author.id, ctx.guild.id)
                try:
                    await ctx.author.send(f"You have set yourself as **afk** with message: ```{message}```")
                except discord.Forbidden:
                    await ctx.reply(f"You have set yourself as **afk**")
def setup(bot):
    bot.add_cog(General(bot))
