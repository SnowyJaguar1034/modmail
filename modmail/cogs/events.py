
import asyncio
import datetime
import json
import logging
from os import access
import re
import io
import aiohttp
import discord
import psutil

from .info import Info
from.core import Core

from discord.ext import commands, tasks
from discord.gateway import DiscordClientWebSocketResponse

from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.model import ButtonStyle

from itertools import cycle

log = logging.getLogger(__name__)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if self.bot.config.testing is False and self.bot.cluster == 1:
            self.bot_stats_updater = bot.loop.create_task(self.bot_stats_updater())
        self.bot_misc_updater = bot.loop.create_task(self.bot_misc_updater())
        self.statuses = []
        self.status.start()

    @tasks.loop(minutes = 5) # seconds = 10
    async def status(self):
        await self.bot.change_presence(activity = discord.Game(next(self.statuses)))
    
    @status.before_loop
    async def before_status(self):
        await self.bot.wait_until_ready()
        data = await self.bot.get_data(448405740797952010)
        users = sum(await self.bot.comm.handler("user_count", self.bot.cluster_count))
        self.statuses = cycle([f'/help | {self.bot.config.default_prefix}help', f'{self.bot.config.activity}', f'{data[13]} is the current count', f'RaidMode is {"Enabled" if data[14] is True else "Disabled"}', f'{data[15]} is the required age for new accounts when raidmode is enabled.', f'Latency: {round(self.bot.latency * 1000, 2)}ms.', f'CPU Usage: {psutil.cpu_percent(interval=None)}%', f'RAM Usage: {psutil.virtual_memory().percent}%', f'I can see {str(users)} users', f'Python Version: {platform.python_version()}', f'Discord.py Version: {discord.__version__}', 'I support slash commands', ])

    @tasks.loop(minutes = 60) # seconds = 10
    async def moderation_logs(self):
        key_words = ["WARN", "MUTE", "UNMUTE", "KICK", "BAN", "UNBAN"] # Add in Captilised versions of each word to account for the Dyno logs
        checked_logs = []
        case_count = 0
        #dict = {}
        moderation = self.bot.get_channel(id = 885569667861717042)
        clifford_log = self.bot.get_channel(id = 500768218257031168)
        # Field One: User who was moderated *
        # Field Two: Moderator who performed the moderation *
        # Field Three: Reason for moderation
        # Field Four: Duration of moderation

        with moderation.channel.typing():
            messages = await clifford_log.channel.history(limit = 10000)#.flatten()
            for message in messages[0:]:
                if message.id not in checked_logs:
                    if message.author.id == 776782769312628746:
                        if len(message.embeds) > 0:
# Need to make the bot look through the msgs chronologically starting at the beginning
                            if key_words in message.embeds[0].title:
                                embed = discord.Embed(title = f"Case {case_count} | {action}", colour = self.bot.config.error_colour, timestamp = message.timestamp)
                                embed.set_author(name = f"{message.embeds[0].fields[0].value} | {message.embeds[0].fields[0].value.id}", icon_url = message.embeds[0].fields[0].value.avatar_url)
                                embed.set_footer(text = f"{message.embeds[0].fields[1].value} | {message.embeds[0].fields[1].value.id}", icon_url = {message.embeds[0].fields[1].value.avatar_url})
                                embed.add_field(name = "Offender", value = message.embeds[0].fields[0].value, inline = True)
                                embed.add_field(name = "Moderator", value = message.embeds[0].fields[1].value, inline = True)
                                if message.embeds[0].fields[3]:
                                    embed.add_field(name = "Duration", value = message.embeds[0].fields[3].value)
                                if message.embeds[0].fields[2]:
                                    embed.add_field(name = "Reason", value = message.embeds[0].fields[2].value)
                                checked_logs.append(message.id)
                                await moderation.send(embed = embed)
        # My embed layout:
            # Author: Moderted User (name and ID) + pfp
            # Title: Case no. | Action
            # Field One: User mention - inline
            # Field Two: Moderator mention - inline
            # Field Three: Duration, if applicable - inline
            # Field Four: Reason, if applicable - not inline
            # Footer: Moderator (name and ID) + pfp


    async def bot_stats_updater(self):
        while True:
            guilds = await self.bot.comm.handler("guild_count", self.bot.cluster_count)
            if len(guilds) < self.bot.cluster_count:
                await asyncio.sleep(300)
                continue
            guilds = sum(guilds)
            await self.bot.session.post(
                f"https://top.gg/api/bots/{self.bot.user.id}/stats",
                data=json.dumps({"server_count": guilds, "shard_count": self.bot.shard_count}),
                headers={"Authorization": self.bot.config.topgg_token, "Content-Type": "application/json"},
            )
            await self.bot.session.post(
                f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats",
                data=json.dumps({"guildCount": guilds, "shardCount": self.bot.shard_count}),
                headers={"Authorization": self.bot.config.dbots_token, "Content-Type": "application/json"},
            )
            await self.bot.session.post(
                f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats",
                data=json.dumps({"guilds": guilds}),
                headers={"Authorization": self.bot.config.dbl_token, "Content-Type": "application/json"},
            )
            await self.bot.session.post(
                f"https://bots.ondiscord.xyz/bot-api/bots/{self.bot.user.id}/guilds",
                data=json.dumps({"guildCount": guilds}),
                headers={"Authorization": self.bot.config.bod_token, "Content-Type": "application/json"},
            )
            await self.bot.session.post(
                f"https://botsfordiscord.com/api/bot/{self.bot.user.id}",
                data=json.dumps({"server_count": guilds}),
                headers={"Authorization": self.bot.config.bfd_token, "Content-Type": "application/json"},
            )
            await self.bot.session.post(
                f"https://discord.boats/api/v2/bot/{self.bot.user.id}",
                data=json.dumps({"server_count": guilds}),
                headers={"Authorization": self.bot.config.dboats_token, "Content-Type": "application/json"},
            )
            await asyncio.sleep(900)

    async def bot_misc_updater(self):
        while True:
            async with self.bot.pool.acquire() as conn:
                data = await conn.fetch("SELECT guild, prefix, expiry, expiryctx FROM data")
                bans = await conn.fetch("SELECT identifier, category FROM ban")
                premium = await conn.fetch("SELECT identifier, expiry FROM premium WHERE expiry IS NOT NULL")
                ctx = await self.bot.get_context(cls=data[4])
            for row in data:
                self.bot.all_prefix[row[0]] = row[1]
            self.bot.banned_users = [row[0] for row in bans if row[1] == 0]
            self.bot.banned_guilds = [row[0] for row in bans if row[1] == 1]
            if self.bot.cluster == 1:
                for row in premium:
                    if row[1] < int(datetime.datetime.utcnow().timestamp() * 1000):
                        await self.bot.tools.wipe_premium(self.bot, row[0])
                if data[2] < int(datetime.datetime.utcnow().timestamp() * 1000):
                    await Core(self).close_channel(ctx, "Ticket was set to automatically close.")
            await asyncio.sleep(60)

    async def on_http_request_start(self, session, trace_config_ctx, params):
        trace_config_ctx.start = asyncio.get_event_loop().time()

    async def on_http_request_end(self, session, trace_config_ctx, params):
        elapsed = asyncio.get_event_loop().time() - trace_config_ctx.start
        if elapsed > 1:
            log.info(f"{params.method} {params.url} took {round(elapsed, 2)} seconds")
        route = str(params.url)
        route = re.sub(r"https:\/\/[a-z\.]+\/api\/v[0-9]+", "", route)
        route = re.sub(r"\/[%A-Z0-9]+", "/_id", route)
        route = re.sub(r"\?.+", "", route)
        status = str(params.response.status)
        if not route.startswith("/"):
            return
        self.bot.prom.http.inc({"method": params.method, "route": route, "status": status})



    @commands.Cog.listener()
    async def on_ready(self):
        log.info("\n")
        log.info("--------")
        log.info(f"{self.bot.user.name}#{self.bot.user.discriminator} is online!")
        log.info("--------")
        log.info("\n")
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(self.on_http_request_start)
        trace_config.on_request_end.append(self.on_http_request_end)
        self.bot.http._HTTPClient__session = aiohttp.ClientSession(connector=self.bot.http.connector, ws_response_class=DiscordClientWebSocketResponse, trace_configs=[trace_config],)
        embed = discord.Embed(title = f"[Cluster {self.bot.cluster}] Bot Ready", colour = 0x00FF00, timestamp=datetime.datetime.utcnow(),)
        if self.bot.config.event_channel:
            await self.bot.http.send_message(self.bot.config.event_channel, None, embed=embed.to_dict())
        snowyjaguar = await self.bot.fetch_user(self.bot.config.owner)
        await snowyjaguar.send(embed=embed)
        #await self.bot.change_presence(activity=discord.Game(name=self.bot.config.activity))

    @commands.Cog.listener()
    async def on_shard_ready(self, shard):
        self.bot.prom.events.inc({"type": "READY"})
        embed = discord.Embed(
            title=f"[Cluster {self.bot.cluster}] Shard {shard} Ready",
            colour=0x00FF00,
            timestamp=datetime.datetime.utcnow(),
        )
        if self.bot.config.event_channel:
            await self.bot.http.send_message(self.bot.config.event_channel, None, embed=embed.to_dict())

    @commands.Cog.listener()
    async def on_shard_connect(self, shard):
        self.bot.prom.events.inc({"type": "CONNECT"})
        embed = discord.Embed(
            title=f"[Cluster {self.bot.cluster}] Shard {shard} Connected",
            colour=0x00FF00,
            timestamp=datetime.datetime.utcnow(),
        )
        if self.bot.config.event_channel:
            await self.bot.http.send_message(self.bot.config.event_channel, None, embed=embed.to_dict())

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard):
        self.bot.prom.events.inc({"type": "DISCONNECT"})
        embed = discord.Embed(
            title=f"[Cluster {self.bot.cluster}] Shard {shard} Disconnected",
            colour=0xFF0000,
            timestamp=datetime.datetime.utcnow(),
        )
        if self.bot.config.event_channel:
            await self.bot.http.send_message(self.bot.config.event_channel, None, embed=embed.to_dict())

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard):
        self.bot.prom.events.inc({"type": "RESUME"})
        embed = discord.Embed(
            title=f"[Cluster {self.bot.cluster}] Shard {shard} Resumed",
            colour=self.bot.config.primary_colour,
            timestamp=datetime.datetime.utcnow(),
        )
        if self.bot.config.event_channel:
            await self.bot.http.send_message(self.bot.config.event_channel, None, embed=embed.to_dict())

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.bot.prom.guilds_join.inc({})
        embed = discord.Embed(title = "Server Join", description = f"{guild.name} ({guild.id})", colour = 0x00FF00, timestamp = datetime.datetime.utcnow(),)
        guilds = sum(await self.bot.comm.handler("guild_count", self.bot.cluster_count))
        embed.set_footer(text = f"{guilds} servers")
        if self.bot.config.join_channel:
            await self.bot.http.send_message(self.bot.config.join_channel, None, embed = embed.to_dict())
        if guild.id in self.bot.banned_guilds:
            await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot.prom.guilds_leave.inc({})
        async with self.bot.pool.acquire() as conn:
            await conn.execute("DELETE FROM data WHERE guild=$1", guild.id)
        embed = discord.Embed(title = "Server Leave", description = f"{guild.name} ({guild.id})",colour = 0xFF0000, timestamp = datetime.datetime.utcnow(),)
        guilds = sum(await self.bot.comm.handler("guild_count", self.bot.cluster_count))
        embed.set_footer(text = f"{guilds} servers")
        if self.bot.config.join_channel:
            await self.bot.http.send_message(self.bot.config.join_channel, None, embed=embed.to_dict())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await self.bot.get_data(member.guild.id)
        log = self.bot.get_channel(id = data[18])
        general = self.bot.get_channel(id = 448408754355175426) # General channel
        off_topic = self.bot.get_channel(id = 828293592585207839) # off topic channel
        staff_commands = self.bot.get_channel(id = 501004576866959391) # Server Manager channel
        server_info = self.bot.get_channel(id = 500413330368888882) # Server Info channel
        raid = self.bot.get_channel(id = data[16])
        acc_age = datetime.datetime.utcnow() - member.created_at
        joincount = await self.bot.get_member_guild(member.id, member.guild.id)
        count = joincount[2] + 1
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE membersguilds SET joincount=$1 WHERE member=$2 and guild=$3", count, member.id, member.guild.id)
        await asyncio.sleep(2)

        member_status = "No status" if member.activity is None else member.activity.name

        embed = discord.Embed(title = f"Member Joined!", description = f"{member.mention} joined {member.guild.name}", colour = self.bot.config.user_colour)
        embed.set_author(name = f"{member.name}#{member.discriminator} | {member.id}", icon_url = member.avatar_url)
        embed.set_thumbnail(url = member.avatar_url)
        embed.set_footer(text = f"Members: {member.guild.member_count}")
        embed.add_field(name = f"Status **{member.status}**", value = f"*{member_status}*", inline = False)
        await Info(self).timestamps(member, embed, True)

        if member.id not in self.bot.config.admins:
            content = f"{member.id}"
            Direct_Message = discord.Embed(title = "Useful Information", description = f" Hey {member.mention} you have joined {member.guild}.\nIf you need to read the community guidelines again you can find them in the {server_info.mention} channel at the top of the channel list in the <#736235918339604491> category.", colour = self.bot.config.branding_colour)
            Direct_Message.set_footer(text = f"DM me {self.bot.user} here if you need to contact staff.")
            join_msg = await log.send(content = content, embed = embed)
            try:
                await member.send(embed = Direct_Message)
            except discord.Forbidden:
                content = content + f"\nI was unable to DM {member} due to their DM's being closed."
                await join_msg.edit(embed = embed, content = content)
                await log.send(f"{member.id}")

            if member.bot == False:
                await general.send(f"{member} Welcome to GTA Online Friendly Sessions, Thank you for joining")
            else:
                tmp = [] # some temp list to append the role objects in
                tmp.append(discord.Object(719518142086512651))
                await member.add_roles(*tmp, reason = f"{member} is a bot!", atomic = True)
                #async for entry in member.guild.audit_logs(action = discord.AuditLogAction.bot_add):
                #print(f'{0.user} added {0.target}')
                await staff_commands.send(f"{member.mention} was added.\n**Status:** {member_status}")

        
        if all([
            data[14] == True, 
            member.guild.id == data[0], 
            acc_age < datetime.timedelta(days = data[15])
        ]):
            if joincount[2] > 3:
                embed = discord.Embed(title = "Member Banned!", description = f'{member}\'s account is **{acc_age.days}** days old and has joined the server **{joincount[2]}** times so the member was banned by raidmode.')
                await member.ban(reason = f"Raidmode enabled: {member}\'s account was deemeed too new by your raidmode configuration. The required age is {data[15]} days old and this users account is {acc_age.days} days old. You can check the current required age with the modconfig command. This user has also joined the server {joincount[2]} times which resulted in their ban.")
                msg = await raid.send(embed = embed)
                try:
                    await member.send(f"This server has raidmode **active** and requires users have a account that is older than **{data[15]}** days old and to have not joined more than **3** times. As your account is less than the servers threshold and you have joined {joincount[2]} times you have been banned.")
                except discord.Forbidden:
                    await msg.edit("{member.id}", embed = embed, content = f"I was unable to DM {member} due to their DM's being closed.")
            else:
                embed = discord.Embed(title = "Member Kicked!", description = f'{member.name}#{member.discriminator} account is **{acc_age.days}** days old and so the member was kicked by raidmode.')
                await member.kick(reason = f"Raidmode enabled: {member}'s account was deemeed too new by your raidmode configuration. The required age is {data[15]} days old and this users account is {acc_age.days} days old. You can check the current required age with the modconfig command.")
                msg = await raid.send(embed = embed)
                try:
                    await member.send(f"This server has raidmode **active** and requires users have a account that is older than **{data[15]}** days old. As your account is less than the servers threshold you have been kicked.")
                except discord.Forbidden:
                    await msg.edit(embed = embed, content = f"I was unable to DM {member} due to their DM's being closed.")
        
        zalgo = re.search("/[\xCC\xCD]/", member.name)
        if zalgo:
            plain = ''.join(filter(str.isalnum, member.name))
            await member.edit(reason = "{member}'s nickname was changed to {plain}because Zalgo text was detected.", nick = plain)
        
        if "discord.gg/" in member.activity.name:
            try:
                await member.send("We identified a disord server invite link in your status message, Kindly change it before moderaton action is taken against you.")
            except discord.HTTPException:
                error = await off_topic.send(f"{member.mention} we were unable to DM you this message due to your DMs being closed\n\n> We identified a disord server invite link in your status message, Kindly change it before moderaton action is taken against you.\n\nThis message will be delted as soon as you react with <a:akoalathumbsup:895039904764026880>")
                await error.add_reaction("<a:akoalathumbsup:895039904764026880>")
                
                def check(payload):
                    return payload.member == member and str(payload.emoji) == '<a:akoalathumbsup:895039904764026880>'
                
                payload = await self.bot.wait_for('raw_reaction_add', check = check)
                await error.delete()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = await self.bot.get_data(member.guild.id)
        log = self.bot.get_channel(id = data[18])
        general = self.bot.get_channel(id = 448408754355175426) # General channel
        snowyjaguar = self.bot.get_user(self.bot.config.owner)
        member_status = "No status" if member.activity is None else member.activity.name
        embed = discord.Embed(title = f"Member left!", description = f"{member.mention} left {member.guild.name}", colour = self.bot.config.mod_colour)
        embed.set_author(name = f"{member.name}#{member.discriminator} | {member.id}", icon_url = member.avatar_url)
        embed.set_thumbnail(url = member.avatar_url)
        embed.set_footer(text = f"Members: {member.guild.member_count}")
        embed.add_field(name = f"Status **{member.status}**", value = f"*{member_status}*", inline = False)
        await Info(self).timestamps(member, embed, True)

        if member.id not in self.bot.config.admins:
            await log.send(f"{member.id}", embed = embed)
            if member.bot == False:
                await general.send(f"{member} left :sob:")
            else:
                await snowyjaguar.send(f"{member} was removed from {member.guild}.")
        else:
            invite = await self.bot.comm.handler("invite_guild", -1, {"guild_id": member.guild.id})
            if not invite:
                await member.send(embed = discord.Embed(description = "No permissions to create an invite link.", colour = self.bot.primary_colour))
            else:
                buttons = [create_button(style = ButtonStyle.blue.URL, url = f"https://discord.gg/{invite.code}", label = f"Invite Code: {invite.code}")]
                action_row = create_actionrow(*buttons)

                await member.send(content = f"You can rejoin {member.guild} by clicking the button", components = [action_row])
                button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
                await button_ctx.edit_origin(content = "You pressed a button!")


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        booster_channel = discord.utils.get(after.guild.text_channels, id = 851793810086166568)
        bwelcome = 851793924372693022
        booster_welcome = discord.utils.get(after.guild.text_channels, id = bwelcome)
        booster_role = discord.utils.get(after.guild.roles, id = 769898504591769610)
        general = discord.utils.get(after.guild.text_channels, id = 448408754355175426)
        promo = discord.utils.get(after.guild.roles, id = 797166495993692160)
        promo_channel = discord.utils.get(after.guild.text_channels, id = 783337245364322344)

        booster = discord.Embed(title = f"Welcome {after.name}#{after.discriminator}", description = f"Thank you for choosing to boost {after.guild.name}.\nYou can head over to <#{bwelcome}> to see the awesome perks you now have.", colour = self.bot.config.booster_colour)
        if booster_role in after.roles and booster_role not in before.roles:
            await general.send(f"{after.name}#{after.discriminator} just boosted the server!<:booster:834372178958745600>")
            await booster_channel.send(f"{after.mention}", embed = booster)
        
        for role in after.roles:
            if all([
                role not in before.roles,
                role.id in self.bot.config.rewards[2:],
                datetime.datetime.utcnow() - after.joined_at >= datetime.timedelta(days = 7),
                datetime.datetime.utcnow() - after.created_at >= datetime.timedelta(weeks = 10), # 2.5 months
                promo not in before.roles,
                ]):
                await after.add_roles(promo, reason = f"{after} received the {promo} role as they meet all of the criteria.", atomic = True)
                await general.send(f"{after} can now send messages in {promo_channel.mention}")
                await after.send(f"Hey, you can now send promotional messages in {promo_channel.mention}.")


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        data = await self.bot.get_data(before.guild.id)
        log = discord.utils.get(after.guild.text_channels, id = data[24])
        if before.content != after.content:
            embed = discord.Embed(title = "📝 Message Edited", description = f"{after.author.display_name} edited a message in {after.channel.mention} ||`{after.channel}`||", colour = after.author.colour, url = after.jump_url, timestamp = datetime.datetime.utcnow())
            embed.set_author(name = f"{after.author} | {after.author.id}", icon_url = after.author.avatar_url)
            embed.add_field(name = "Old Message:", value = f"{before.content}", inline = False)
            embed.add_field(name = "New Message:", value = f"{after.content}", inline = False)
            embed.set_footer(text = f"Message ID: {after.id}.")
            await log.send(embed = embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        data = await self.bot.get_data(message.guild.id)
        log = discord.utils.get(message.guild.text_channels, id = data[23])
        embed = discord.Embed(title = "🗑 Message Deleted", description = f"{message.author.display_name} deleted a message in {message.channel.mention} ||`{message.channel}`||", colour = message.author.colour, timestamp = datetime.datetime.utcnow())
        embed.set_author(name = f"{message.author} | {message.author.id}", icon_url = message.author.avatar_url)
        embed.add_field(name = "Content", value = f"{message.content}", inline = False)
        embed.set_footer(text = f"Message ID: {message.id}.")
        await log.send(embed = embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        history = ""
        authors = ""
        authors_sorted = []
        for message in messages:
            server = message.guild.id
            channel = message.channel
            history = (f"[{str(message.created_at.replace(microsecond=0))}] Author: {message.author} Message: ({message.id}) {message.content}\n\n" + history)
        data = await self.bot.get_data(server)
        log = self.bot.get_channel(data[23])
        embed = discord.Embed(title = "A bulk message deletion occured.", description = f"**{len(messages)}** messages were deleted from {channel.mention} ||`{channel}`||.", colour = message.author.colour, timestamp = datetime.datetime.utcnow())
        embed.set_footer(text = f"Channel {channel} | {channel.id}.")

        history = io.StringIO(history)
        file = discord.File(history, f"[{datetime.datetime.utcnow().strftime('%d.%m.%Y %I.%M.%S %p')}] {channel} Bulk Message Deletion.txt") # replace(microsecond=0)
        await log.send(embed = embed, file = file)
        
    """
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        data = await self.bot.get_data(payload.guild_id) # Accessing data from main table
        starboard = self.bot.get_channel(data[27]) # Pulling the starboard ID from main table and making it a channel object
        stars = await self.bot.get_star(payload.message_id) # Accessing from the starboard table
        #star_reactions = ["⭐", ":questionable_star:", ":star_struck:", ":star2:", ":StarPiece:", ":purple_star:"] # Listing the approved reactions to watch for
        reactions_count = stars[3] # Inilizing a reaction count
        with starboard.typing():
            for star in self.bot.config.star_reactions: # Checking each option in the approved reactions
                if payload.emoji.name == star: # Checking if the reaction used is in the approved list
                    stared_message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id) # Getting the the original msg as a message object

                    if not stared_message.author.bot and payload.member.id != stared_message.author.id: # Checking the person adding the reaction isn't a bot and/or that they aren't the person who sent the orginal message.
                        reactions_count = stars[1] + 1

                        # Declaring the Embed to post in the starboard channel
                        embed = discord.Embed(title = f"Starred message", description = f"{stared_message.content}" or "See attachment", colour = stared_message.author.colour, url = stared_message.jump_url, timestamp = datetime.datetime.utcnow())
                        if len(stared_message.attachments): # Checking if the orignal message contained a image
                            embed.set_image(url = stared_message.attachments[0].url) # Add the orginal msgs image to the embed
                        embed.set_author(name = stared_message.author, icon_url = stared_message.author.avatar_url)

                        if stared_message.id not in stars[0]: # Checking if the orignal message ID is NOT stored in the db
                            post = await starboard.send(embed = embed, content = f"Stars: {str(reactions_count)}") # Sending the embed to the starboard
                            async with self.bot.pool.acquire() as conn:
                                await conn.execute("UPDATE starboard SET Stared=$1 WHERE Post=$2, Count=$3", stared_message.id, post.id, reactions_count)
                        else:
                            temp = discord.Object(stars[2])
                            post = await self.bot.get_channel(starboard.id).fetch_message(temp) # Getting the the post msg as a message object
                            async with self.bot.pool.acquire() as conn:
                                await conn.execute("UPDATE starboard SET Count=$1", reactions_count)
                            await post.edit(embed = embed, content = f"Stars: {str(reactions_count)}")
                        
                    else:
                        await stared_message.remove_reaction(payload.emoji, payload.member)
    """

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if user.id in self.bot.config.admins:
            await user.unban(reason = "This account is a test acount for SnowyJaguar#1034")


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild != None:
            data = await self.bot.get_data(message.guild.id)
            afk_return = await self.bot.get_member_guild(message.author.id, message.guild.id)
            if afk_return[4] == True:
                async with self.bot.pool.acquire() as conn:
                    await conn.execute("UPDATE membersguilds SET afk=$1, afkmessage=$2 WHERE member=$3 and guild=$4", False, None, message.author.id, message.guild.id)
                await message.reply(f"Welcome back {message.author.mention}")        
            if message.mentions:
                for mention in message.mentions:
                    afk = await self.bot.get_member_guild(mention.id, message.guild.id)
                    if afk[4] == True:
                        await message.channel.send(f"{mention} is AFK:\n\t{afk[5]}:")
            server_info = self.bot.get_channel(id = 500413330368888882) # Server Info channel
            text = f"Please don't mention `@everyone` unnecessarily. If you want to ping a large group of members we have roles for activities or games which can be found in {server_info.mention} or you could ping `@here`."
            print(f"\nMessage event 1: {message.content}\n{message}")
            if bad := [word for word in data[28] or self.bot.config.default_bad_words if word in message.content]:
            #if message.content in data[28] or message.content in self.bot.config.default_bad_words:
                #if message.author.has_any_role(data[3]) or message.author.has_guild_permissions(self.bot.config.moderator_permissions):
                if (len(set(data[3]) & set([role.id for role in message.author.roles])) > 0) or self.bot.config.moderator_permissions in message.author.guild_permissions:
                    return
                else:
                    print(f"\nMessage event: {message.content}\n{message}")
                    await message.delete()
                    try:
                        await message.author.send(f'Your message had `{", ".join(bad)}` in it, This word is conssidered a "bad" word on this server so your message was removed.')
                    except discord.HTTPException:
                        await message.channel.send(f'{message.author.mention} `{bad}` is conssidered a "bad" word on this server.')
                    if "@everyone" in message.content:
                    #if message.mention_everyone:
                        try:
                            await message.author.send(text)
                        except discord.HTTPException:
                            await message.channel.send(f'{message.author.mention} {text}')
                    

        
        ctx = await self.bot.get_context(message)
        if not ctx.command:
            return
        self.bot.prom.commands.inc({"name": ctx.command.name})
        if message.guild:
            if message.guild.id in self.bot.banned_guilds:
                await message.guild.leave()
                return
            permissions = message.channel.permissions_for(message.guild.me)
            if permissions.send_messages is False:
                return
            elif permissions.embed_links is False:
                await message.channel.send("The Embed Links permission is needed for basic commands to work.")
                return
        if message.author.id in self.bot.banned_users:
            await ctx.send(
                embed=discord.Embed(description="You are banned from the bot.", colour=self.bot.error_colour)
            )
            return
        if ctx.command.cog_name in ["Owner", "Admin"] and (
            ctx.author.id in self.bot.config.admins or ctx.author.id in self.bot.config.owners
        ):
            embed = discord.Embed(
                title=ctx.command.name.title(),
                description=ctx.message.content,
                colour=self.bot.primary_colour,
                timestamp=datetime.datetime.utcnow(),
            )
            embed.set_author(name=f"{ctx.author} ({ctx.author.id})", icon_url=ctx.author.avatar_url)
            if self.bot.config.admin_channel:
                await self.bot.http.send_message(self.bot.config.admin_channel, None, embed=embed.to_dict())
        if ctx.prefix == f"<@{self.bot.user.id}> " or ctx.prefix == f"<@!{self.bot.user.id}> ":
            ctx.prefix = self.bot.tools.get_guild_prefix(self.bot, message.guild)
        await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_socket_response(self, message):
        if message.get("op") == 0:
            t = message.get("t")
            if t == "PRESENCE_UPDATE":
                return
            self.bot.prom.dispatch.inc({"type": t})


def setup(bot):
    bot.add_cog(Events(bot))
