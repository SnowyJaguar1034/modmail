
import asyncio
import copy
import datetime
import io
import logging
import string
import discord

from discord.ext import commands
from utils import checks

log = logging.getLogger(__name__)


class DirectMessageEvents(commands.Cog, name = "Direct Message"):
    def __init__(self, bot):
        self.bot = bot
        self.guild = None

    async def send_mail(self, message, guild, to_send):
        self.bot.prom.tickets_message.inc({})
        guild2 = guild
        guild = await self.bot.comm.handler("get_guild", -1, {"guild_id": guild})
        if not guild:
            await message.channel.send(embed = discord.Embed(description = "The server was not found.", colour = self.bot.error_colour))
            return
        member = await self.bot.comm.handler("get_guild_member",-1,{"guild_id": guild.id, "member_id": message.author.id})
        if not member:
            await message.channel.send(embed = discord.Embed(description = "You are not in that server, and the message is not sent.", colour = self.bot.error_colour,))
            return
        ''' 
        try:
            member = await guild.fetch_member(message.author.id)
        except discord.NotFound:
            await message.channel.send(embed = discord.Embed("You are not in that server, and the message is not sent.")
            )
            return
         '''
        data = await self.bot.get_data(guild.id)
        category = await self.bot.comm.handler(
            "get_guild_channel",
            -1,
            {"guild_id": guild.id, "channel_id": data[2]},
        )
        if not category:
            await message.channel.send(embed = discord.Embed(description = "A ModMail category is not found. The bot is not set up properly in the server.", colour = self.bot.error_colour,))
            return
        if message.author.id in data[9]:
            await message.channel.send(embed = discord.Embed(description = "That server has blacklisted you from sending a message there.", colour = self.bot.error_colour,))
            return
        channels = [
            channel
            for channel in guild.text_channels
            if checks.is_modmail_channel2(self.bot, channel, message.author.id)
        ]
        #_channel = channels[0].id
        channel_id = None
        new_ticket = False
        if len(channels) > 0:
            channel_id = channels[0].id
        if not channel_id:
            self.bot.prom.tickets.inc({})
            try:
                name = "".join(
                    x for x in message.author.name.lower() if x not in string.punctuation and x.isprintable()
                )
                if name:
                    name = name + f"-{message.author.discriminator}"
                else:
                    name = message.author.id
                channel_id = (await self.bot.http.create_channel(guild.id, 0, name = name, parent_id = category.id, topic = f"ModMail Channel {message.author.id} (Please do not change this)",))["id"]
                new_ticket = True
                log_channel = await self.bot.comm.handler(
                    "get_guild_channel",
                    -1,
                    {"guild_id": guild.id, "channel_id": data[4]},
                )
                if log_channel:
                    try:
                        embed = discord.Embed(title = "New Ticket", colour = self.bot.user_colour, timestamp = datetime.datetime.utcnow(),)
                        embed.set_footer(text = f"{message.author.name}#{message.author.discriminator} | {message.author.id}", icon_url = message.author.avatar_url,)
                        await self.bot.http.send_message(log_channel.id, None, embed = embed.to_dict())
                    except discord.Forbidden:
                        pass
            except discord.Forbidden:
                await message.channel.send(embed = discord.Embed(description = "The bot is missing permissions to create a channel. Please contact an admin on the server.", colour = self.bot.error_colour,))
                return
            except discord.HTTPException as e:
                await message.channel.send(embed = discord.Embed(description = f"A HTTPException error occurred. Please contact an admin on the server with the following error information: {e.text} ({e.code}).", colour = self.bot.error_colour,))
                return
        try:
            if new_ticket is True:
                prefix = self.bot.tools.get_guild_prefix(self.bot, guild)
                guild2 = await self.bot.fetch_guild(guild2)
                member2 = await guild2.fetch_member(message.author.id)
                embed = discord.Embed(title = "New Ticket", description = f"Type a message in this channel to reply. Messages starting with the server prefix `{prefix}` are ignored, and can be used for staff discussion. Use the command `{prefix}close [reason]` to close this ticket.", colour = self.bot.primary_colour, timestamp = datetime.datetime.utcnow(),)
                embed.add_field(name = "Roles", value = "*None* " if len(member2._roles) == 0 else ", ".join([f"<@&{role}>" for role in member2._roles]) if len(" ".join([f"<@&{role}>" for role in member2._roles])) <= 1024 else f"*{len(member2._roles)} roles*",)
                embed.set_footer(text = f"{message.author.name}#{message.author.discriminator} | {message.author.id}", icon_url = message.author.avatar_url,)
                roles = []
                for role in data[8]:
                    if role == guild.id:
                        roles.append("@everyone")
                    elif role == -1:
                        roles.append("@here")
                    else:
                        roles.append(f"<@&{role}>")
                await self.bot.http.send_message(channel_id, " ".join(roles), embed=embed.to_dict())
                if data[5]:
                    embed = discord.Embed(title = "Custom Greeting Message", description = self.bot.tools.tag_format(data[5], message.author), colour = self.bot.mod_colour, timestamp = datetime.datetime.utcnow(),)
                    embed.set_footer(text = f"{guild.name} | {guild.id}", icon_url = guild.icon_url)
                    await message.channel.send(embed = embed)
            embed = discord.Embed(title = "Message Sent", description = to_send, colour = self.bot.user_colour, timestamp = datetime.datetime.utcnow(),)
            embed.set_footer(text=f"{guild.name} | {guild.id}", icon_url = guild.icon_url)
            files = []
            for file in message.attachments:
                saved_file = io.BytesIO()
                await file.save(saved_file)
                files.append(discord.File(saved_file, file.filename))
            message2 = await message.channel.send(embed = embed, files = files)
            embed.title = "Message Received"
            embed.set_footer(text = f"{message.author.name}#{message.author.discriminator} | {message.author.id}", icon_url = message.author.avatar_url,)
            for count, attachment in enumerate([attachment.url for attachment in message2.attachments], start=1):
                embed.add_field(name = f"Attachment {count}", value = attachment, inline = False)
            for file in files:
                file.reset()
            if files:
                post = await self.bot.http.send_files(channel_id, embed=embed.to_dict(), files=files)
                #postlocal = await _channel.fetch_message(post)
            else:
                post = await self.bot.http.send_message(channel_id, None, embed=embed.to_dict())
                #postlocal = await _channel.fetch_message(post)
        except discord.Forbidden:
            try:
                await message2.delete()
            except NameError:
                pass
            await message.channel.send(embed = discord.Embed(description = "No permission to send message in the channel. Please contact an admin on the server.", colour = self.bot.error_colour))
        #print(f"\nchannel_id: {type(channel_id)} | {type(channel_id)}\npostlocal: {type(postlocal)}\nmessage2: {type(message2.id)}\n")
        #async with self.bot.pool.acquire() as conn:
            #await conn.execute("UPDATE tickets SET postlocal=$1, postremote=$2, member=$3", postlocal.id, message2.id, message.author.id)

    async def select_guild(self, message, prefix, msg=None):
        data = await self.bot.comm.handler(
            "get_user_guilds", self.bot.cluster_count, {"user_id": message.author.id}
        )
        guilds = []
        for chunk in data:
            guilds.extend(chunk)
        guild_list = {}
        for guild in guilds:
            channels = [
                channel
                for channel in guild.text_channels
                if checks.is_modmail_channel2(self.bot, channel, message.author.id)
            ]
            channel = None
            if len(channels) > 0:
                channel = channels[0]
            if not channel:
                guild_list[str(guild.id)] = (guild.name, False)
            else:
                guild_list[str(guild.id)] = (guild.name, True)
        embeds = []
        current_embed = None
        for guild, value in guild_list.items():
            if not current_embed:
                current_embed = discord.Embed(title = "Select Server", description = "Please select the server you want to send this message to. You can do so by reacting with the corresponding reaction.", colour = self.bot.primary_colour,)
                current_embed.set_footer(text = "Use the reactions to flip pages.")
            current_embed.add_field(name = f"{len(current_embed.fields) + 1}: {value[0]}", value = f"{'Create a new ticket.' if value[1] is False else 'Existing ticket.'}\nServer ID: {guild}",)
            if len(current_embed.fields) == 9:
                embeds.append(current_embed)
                current_embed = None
        if current_embed:
            embeds.append(current_embed)
        if len(embeds) == 0:
            await message.channel.send(embed = discord.Embed(description = "Oops... No server found.", colour = self.bot.primary_colour))
            return
        if msg:
            await msg.edit(embed = embeds[0])
        else:
            msg = await message.channel.send(embed = embeds[0])
        reactions = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "◀", "▶"]

        async def add_reactions(length):
            await msg.add_reaction("◀")
            await msg.add_reaction("▶")
            for index in range(0, length):
                await msg.add_reaction(reactions[index])

        def reaction_check(reaction2, user2):
            return str(reaction2) in reactions and user2.id == message.author.id and reaction2.message.id == msg.id

        await add_reactions(len(embeds[0].fields))
        page_index = 0
        chosen = -1
        try:
            while chosen < 0:
                reaction, _ = await self.bot.wait_for("reaction_add", check = reaction_check, timeout = 60)
                if str(reaction) == "◀":
                    if page_index != 0:
                        page_index = page_index - 1
                        await msg.edit(embed=embeds[page_index])
                        await add_reactions(len(embeds[page_index].fields))
                elif str(reaction) == "▶":
                    if page_index + 1 < len(embeds):
                        page_index = page_index + 1
                        await msg.edit(embed=embeds[page_index])
                        if len(embeds[page_index].fields) != 10:
                            to_remove = reactions[len(embeds[page_index].fields) : -2]
                            msg = await msg.channel.fetch_message(msg.id)
                            for this_reaction in msg.reactions:
                                if str(this_reaction) in to_remove:
                                    await this_reaction.remove(self.bot.user)
                elif reactions.index(str(reaction)) >= 0:
                    chosen = reactions.index(str(reaction))
        except asyncio.TimeoutError:
            await self.remove_reactions(msg)
            await msg.edit(embed=discord.Embed(description = "Time out. You did not choose anything.", colour = self.bot.error_colour))
            return
        await msg.delete()
        guild = embeds[page_index].fields[chosen].value.split()[-1]
        await self.send_mail(message, int(guild), message.content)

    async def remove_reactions(self, message):
        message = await message.channel.fetch_message(message.id)
        for reaction in message.reactions:
            await reaction.remove(self.bot.user)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return
        prefix = self.bot.config.default_prefix
        if message.content.startswith(prefix):
            return
        if message.author.id in self.bot.banned_users:
            await message.channel.send(embed = discord.Embed(description = "You are banned from this bot.", colour = self.bot.error_colour))
            return
        if self.bot.config.default_server:
            await self.send_mail(message, self.bot.config.default_server, message.content)
            return
        guild = None
        async for msg in message.channel.history(limit=30):
            if (
                msg.author.id == self.bot.user.id
                and len(msg.embeds) > 0
                and msg.embeds[0].title in ["Message Received", "Message Sent"]
            ):
                guild = msg.embeds[0].footer.text.split()[-1]
                guild = await self.bot.comm.handler("get_guild", -1, {"guild_id": int(guild)})
                break
        msg = None
        confirmation = await self.bot.tools.get_user_settings(self.bot, message.author.id)
        confirmation = True if confirmation is None or confirmation[1] is True else False
        if guild and confirmation is False:
            await self.send_mail(message, guild.id, message.content)
        elif guild and confirmation is True:
            embed = discord.Embed(title = "Confirmation", description = f"You're sending this message to **{guild.name}** (ID: {guild.id}). React with ✅ to confirm.\nWant to send to another server instead? React with 🔁.\nTo cancel this request, react with ❌.", colour = self.bot.primary_colour,)
            embed.set_footer(text=f"Tip: You can disable confirmation messages with the {prefix}confirmation command.")
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("✅")
            await msg.add_reaction("🔁")
            await msg.add_reaction("❌")

            def reaction_check(reaction2, user2):
                return (
                    str(reaction2) in ["✅", "🔁", "❌"]
                    and user2.id == message.author.id
                    and reaction2.message.id == msg.id
                )

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", check=reaction_check, timeout=60)
            except asyncio.TimeoutError:
                await self.remove_reactions(msg)
                await msg.edit(embed = discord.Embed(description = "Time out. You did not choose anything.", colour = self.bot.error_colour,))
                return
            if str(reaction) == "✅":
                await msg.delete()
                await self.send_mail(message, guild.id, message.content)
            elif str(reaction) == "🔁":
                await self.remove_reactions(msg)
                await self.select_guild(message, prefix, msg)
            elif str(reaction) == "❌":
                await self.remove_reactions(msg)
                await msg.edit(embed=discord.Embed(description = "Request cancelled successfully.", colour = self.bot.error_colour))
                await asyncio.sleep(5)
                await msg.delete()
        else:
            await self.select_guild(message, prefix)

    @commands.dm_only()
    @commands.command(description = "Send message to another server, useful when confirmation messages are disabled.", usage = "new <message>", aliases = ["create", "switch", "change"],)
    async def new(self, ctx, *, message):
        msg = copy.copy(ctx.message)
        msg.content = message
        await self.select_guild(msg, ctx.prefix)

    #"""
    @commands.dm_only()
    @commands.command(description = "Shortcut to send message to a server.", usage = "send <server ID> <message>")
    async def send(self, ctx, guild: int, *, message: str):
        await self.send_mail(ctx.message, guild, message)
    #"""

    @checks.is_mod()
    @commands.guild_only()
    @commands.command(description = "Create ticket for a member.", usage = "<member> <message>")
    async def createticket(self, ctx, member: discord.Member, *, message: str):
        member = ctx.author.id if ctx.author.id == member.id else member
        #await self.send_mail(ctx.message, member.guild.id, message)
        data = await self.bot.get_data(ctx.guild.id)
        category = await self.bot.comm.handler(
            "get_guild_channel",
            -1,
            {"guild_id": ctx.guild.id, "channel_id": data[2]},
        )
        if not category:
            await message.channel.send(embed = discord.Embed(description = "A ModMail category is not found. The bot is not set up properly in the server.", colour = self.bot.error_colour,))
            return
        channels = [channel for channel in ctx.guild.text_channels if checks.is_modmail_channel2(self.bot, channel, ctx.author.id)]
        channel_id = None
        new_ticket = False
        if len(channels) > 0:
            channel_id = channels[0].id
        if not channel_id:
            self.bot.prom.tickets.inc({})
            try:
                name = "".join(
                    x for x in member.name.lower() if x not in string.punctuation and x.isprintable()
                )
                if name:
                    name = name + f"-{member.discriminator}"
                else:
                    name = member.id
                channel_id = (await self.bot.http.create_channel(
                    ctx.guild.id,
                    0,
                    name = name,
                    parent_id = category.id,
                    topic = f"ModMail Channel {member.id} (Please do not change this)",
                ))["id"]
                new_ticket = True
                log_channel = await self.bot.comm.handler(
                    "get_guild_channel",
                    -1,
                    {"guild_id": ctx.guild.id, "channel_id": data[4]},
                )
                if log_channel:
                    try:
                        embed = discord.Embed(title = "New Ticket", colour = self.bot.user_colour, timestamp = datetime.datetime.utcnow(),)
                        embed.set_footer(text = f"{member.name}#{member.discriminator} | {member.id}", icon_url = member.avatar_url,)
                        await self.bot.http.send_message(log_channel.id, None, embed = embed.to_dict())
                    except discord.Forbidden:
                        pass
            except discord.Forbidden:
                await member.send(embed = discord.Embed(description = "The bot is missing permissions to create a channel. Please contact an admin on the server.", colour = self.bot.error_colour,))
                return
            except discord.HTTPException as e:
                await member.send(embed = discord.Embed(description = f"A HTTPException error occurred. Please contact an admin on the server with the following error information: {e.text} ({e.code}).", colour = self.bot.error_colour,))
                return
        try:
            if new_ticket is True:
                prefix = self.bot.tools.get_guild_prefix(self.bot, ctx.guild)
                #guild2 = await self.bot.fetch_guild(guild2)
                #member = await ctx.guild.fetch_member(member)
                embed = discord.Embed(title = "New Ticket", description = f"Type a message in this channel to reply. Messages starting with the server prefix `{prefix}` are ignored, and can be used for staff discussion. Use the command `{prefix}close [reason]` to close this ticket.", colour = self.bot.primary_colour, timestamp = datetime.datetime.utcnow(),)
                embed.add_field(name = "Roles", value = "*None* " if len(member._roles) == 0 else ", ".join([f"<@&{role}>" for role in member._roles]) if len(" ".join([f"<@&{role}>" for role in member._roles])) <= 1024 else f"*{len(member._roles)} roles*",)
                embed.set_footer(text = f"{member.name}#{member.discriminator} | {member.id}", icon_url = member.avatar_url,)
                roles = []
                for role in data[8]:
                    if role == ctx.guild.id:
                        roles.append("@everyone")
                    elif role == -1:
                        roles.append("@here")
                    else:
                        roles.append(f"<@&{role}>")
                await self.bot.http.send_message(channel_id, " ".join(roles), embed=embed.to_dict())
                if data[5]:
                    embed = discord.Embed(title = "Custom Greeting Message", description = self.bot.tools.tag_format(data[5], member), colour = self.bot.mod_colour, timestamp = datetime.datetime.utcnow(),)
                    embed.set_footer(text = f"{ctx.guild.name} | {ctx.guild.id}", icon_url = ctx.guild.icon_url)
                    await member.send(embed = embed)
            embed = discord.Embed(title = "Message Sent", description = message, colour = self.bot.user_colour, timestamp = datetime.datetime.utcnow(),)
            embed.set_footer(text=f"{ctx.guild.name} | {ctx.guild.id}", icon_url = ctx.guild.icon_url)
            files = []
            for file in ctx.message.attachments:
                saved_file = io.BytesIO()
                await file.save(saved_file)
                files.append(discord.File(saved_file, file.filename))
            message2 = await member.send(embed = embed, files = files)
            embed.title = "Message Received"
            embed.set_footer(text = f"{member.name}#{member.discriminator} | {member.id}", icon_url = member.avatar_url,)
            for count, attachment in enumerate([attachment.url for attachment in message2.attachments], start=1):
                embed.add_field(name = f"Attachment {count}", value = attachment, inline = False)
            for file in files:
                file.reset()
            if files:
                await self.bot.http.send_files(channel_id, embed=embed.to_dict(), files=files)
            else:
                await self.bot.http.send_message(channel_id, None, embed=embed.to_dict())
        except discord.Forbidden:
            try:
                await message2.delete()
            except NameError:
                pass
            await member.send(embed = discord.Embed(description = "No permission to send message in the channel. Please contact an admin on the server.", colour = self.bot.error_colour))

    @checks.is_mod()
    @commands.guild_only()
    @commands.command(description = "lets members make a ticket on the server, Conversations still happen in DMs.", usage = "<message>")
    async def ticket(self, ctx, *, message: str):
        data = await self.bot.get_data(ctx.guild.id)
        category = await self.bot.comm.handler(
            "get_guild_channel",
            -1,
            {"guild_id": ctx.guild.id, "channel_id": data[2]},
        )
        if not category:
            await message.channel.send(embed = discord.Embed(description = "A ModMail category is not found. The bot is not set up properly in the server.", colour = self.bot.error_colour,))
            return
        channels = [channel for channel in ctx.guild.text_channels if checks.is_modmail_channel2(self.bot, channel, ctx.author.id)]
        channel_id = None
        new_ticket = False
        if len(channels) > 0:
            channel_id = channels[0].id
        if not channel_id:
            self.bot.prom.tickets.inc({})
            try:
                name = "".join(
                    x for x in ctx.author.name.lower() if x not in string.punctuation and x.isprintable()
                )
                if name:
                    name = name + f"-{ctx.author.discriminator}"
                else:
                    name = ctx.author.id
                channel_id = (await self.bot.http.create_channel(
                    ctx.guild.id,
                    0,
                    name = name,
                    parent_id = category.id,
                    topic = f"ModMail Channel {ctx.author.id} (Please do not change this)",
                ))["id"]
                new_ticket = True
                log_channel = await self.bot.comm.handler(
                    "get_guild_channel",
                    -1,
                    {"guild_id": ctx.guild.id, "channel_id": data[4]},
                )
                if log_channel:
                    try:
                        embed = discord.Embed(title = "New Ticket", colour = self.bot.user_colour, timestamp = datetime.datetime.utcnow(),)
                        embed.set_footer(text = f"{ctx.author.name}#{ctx.author.discriminator} | {ctx.author.id}", icon_url = ctx.author.avatar_url,)
                        await self.bot.http.send_message(log_channel.id, None, embed = embed.to_dict())
                    except discord.Forbidden:
                        pass
            except discord.Forbidden:
                await ctx.author.send(embed = discord.Embed(description = "The bot is missing permissions to create a channel. Please contact an admin on the server.", colour = self.bot.error_colour,))
                return
            except discord.HTTPException as e:
                await ctx.author.send(embed = discord.Embed(description = f"A HTTPException error occurred. Please contact an admin on the server with the following error information: {e.text} ({e.code}).", colour = self.bot.error_colour,))
                return
        try:
            if new_ticket is True:
                prefix = self.bot.tools.get_guild_prefix(self.bot, ctx.guild)
                #guild2 = await self.bot.fetch_guild(guild2)
                #member = await ctx.guild.fetch_member(member)
                embed = discord.Embed(title = "New Ticket", description = f"Type a message in this channel to reply. Messages starting with the server prefix `{prefix}` are ignored, and can be used for staff discussion. Use the command `{prefix}close [reason]` to close this ticket.", colour = self.bot.primary_colour, timestamp = datetime.datetime.utcnow(),)
                embed.add_field(name = "Roles", value = "*None* " if len(ctx.author._roles) == 0 else ", ".join([f"<@&{role}>" for role in ctx.author._roles]) if len(" ".join([f"<@&{role}>" for role in ctx.author._roles])) <= 1024 else f"*{len(ctx.author._roles)} roles*",)
                embed.set_footer(text = f"{ctx.author.name}#{ctx.author.discriminator} | {ctx.author.id}", icon_url = ctx.author.avatar_url,)
                roles = []
                for role in data[8]:
                    if role == ctx.guild.id:
                        roles.append("@everyone")
                    elif role == -1:
                        roles.append("@here")
                    else:
                        roles.append(f"<@&{role}>")
                await self.bot.http.send_message(channel_id, " ".join(roles), embed=embed.to_dict())
                if data[5]:
                    embed = discord.Embed(title = "Custom Greeting Message", description = self.bot.tools.tag_format(data[5], ctx.author), colour = self.bot.mod_colour, timestamp = datetime.datetime.utcnow(),)
                    embed.set_footer(text = f"{ctx.guild.name} | {ctx.guild.id}", icon_url = ctx.guild.icon_url)
                    await ctx.author.send(embed = embed)
            embed = discord.Embed(title = "Message Sent", description = message, colour = self.bot.user_colour, timestamp = datetime.datetime.utcnow(),)
            embed.set_footer(text=f"{ctx.guild.name} | {ctx.guild.id}", icon_url = ctx.guild.icon_url)
            files = []
            for file in ctx.message.attachments:
                saved_file = io.BytesIO()
                await file.save(saved_file)
                files.append(discord.File(saved_file, file.filename))
            message2 = await ctx.author.send(embed = embed, files = files)
            embed.title = "Message Received"
            embed.set_footer(text = f"{ctx.author.name}#{ctx.author.discriminator} | {ctx.author.id}", icon_url = ctx.author.avatar_url,)
            for count, attachment in enumerate([attachment.url for attachment in message2.attachments], start=1):
                embed.add_field(name = f"Attachment {count}", value = attachment, inline = False)
            for file in files:
                file.reset()
            if files:
                await self.bot.http.send_files(channel_id, embed=embed.to_dict(), files=files)
            else:
                await self.bot.http.send_message(channel_id, None, embed=embed.to_dict())
        except discord.Forbidden:
            try:
                await message2.delete()
            except NameError:
                pass
            await ctx.author.send(embed = discord.Embed(description = "No permission to send message in the channel. Please contact an admin on the server.", colour = self.bot.error_colour))
        await ctx.message.delete()

    

    @commands.dm_only()
    @commands.command(description = "Enable or disable the confirmation message.", usage = "confirmation")
    async def confirmation(self, ctx):
        data = await self.bot.tools.get_user_settings(self.bot, ctx.author.id)
        if not data or data[1] is True:
            async with self.bot.pool.acquire() as conn:
                if not data:
                    await conn.execute(
                        "INSERT INTO preference (identifier, confirmation) VALUES ($1, $2)",
                        ctx.author.id,
                        False,
                    )
                else:
                    await conn.execute(
                        "UPDATE preference SET confirmation=$1 WHERE identifier=$2",
                        False,
                        ctx.author.id,
                    )
            await ctx.send(embed = discord.Embed(description = f"Confirmation messages are disabled. To send messages to another server, use `{ctx.prefix}new <message>`.", colour = self.bot.primary_colour,)) #  or `{ctx.prefix}send <server ID> <message>`
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute(
                "UPDATE preference SET confirmation=$1 WHERE identifier=$2",
                True,
                ctx.author.id,
            )
        await ctx.send(embed = discord.Embed(description = "Confirmation messages are enabled.", colour = self.bot.primary_colour))

def setup(bot):
    bot.add_cog(DirectMessageEvents(bot))
