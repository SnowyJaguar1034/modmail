import asyncio
import logging
import typing
import discord

from discord.ext import commands
from discord.utils import get
from utils import checks
from datetime import datetime, timedelta
from typing import Optional, Union

log = logging.getLogger(__name__)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.raid_permission = discord.PermissionOverwrite(send_messages = False, add_reactions = False, use_slash_commands = False)
        self.unraid_permission = discord.PermissionOverwrite(send_messages = True, add_reactions = False, use_slash_commands = False)

    @commands.check_any(commands.has_permissions(manage_guild = True), commands.has_permissions(manage_messages = True), commands.has_permissions(manage_channels = True))
    @commands.guild_only()
    @commands.command(description = f"**Enables** and **Disbales** the auto kicking system which kicks new members who don't meet the account age requirement. You can check the current state by using `modconfig`", alaises = ["raid", "unraid", "autokick", "auto-kick", "activiateraidmode", "deactivateraidmode", "activate-raidmode", "deactivate-raidmode"])
    async def raidmode(self,ctx):
        data = await self.bot.get_data(ctx.guild.id)
        if data[14] == False:
            async with self.bot.pool.acquire() as conn:
                await conn.execute("UPDATE data SET raidmode=$1 WHERE guild=$2", True if data[14] is False else False, ctx.guild.id,)
            #self.raidmode = True
            await ctx.send("Raidmode has been enabled!")
        elif data[14] == True:
            async with self.bot.pool.acquire() as conn:
                await conn.execute("UPDATE data SET raidmode=$1 WHERE guild=$2", False if data[14] is True else False, ctx.guild.id,)
            #self.raidmode = False
            await ctx.send("Raidmode has been disabled!")

    @commands.check_any(commands.has_permissions(manage_guild = True), commands.has_permissions(manage_messages = True), commands.has_permissions(manage_channels = True))
    @checks.in_database()
    @commands.guild_only()
    @commands.command(description = "Locks all text channels.", alaises = ["lock"])
    async def lockdown(self, ctx):
        data = await self.bot.get_data(ctx.guild.id)
        for roles in data[11]:
            role = get(ctx.guild.roles, id = roles)
            permission = role.permissions
            permission.Update(send_messages = False)
            permission.Update(add_reactions = False)
            permission.Update(use_slash_commands = False)
            await role.edit(reason = f"{ctx.author} activated raidmode.", permissions = permission)
            await ctx.guild.edit(reason = f"{ctx.author} activated raidmode.", verification_level = discord.VerificationLevel.extreme)
        await ctx.send("Server locked")

    @commands.check_any(commands.has_permissions(manage_guild = True), commands.has_permissions(manage_messages = True), commands.has_permissions(manage_channels = True))
    @checks.in_database()
    @commands.guild_only()
    @commands.command(description = "Unlocks all text channels.", alaises = ["endlockdown", "unlock"])
    async def unlockdown(self,ctx):
        data = await self.bot.get_data(ctx.guild.id)
        for roles in data[11]:
            role = get(ctx.guild.roles, id = roles)
            permission = role.permissions
            permission.Update(send_messages = True)
            permission.Update(add_reactions = True)
            permission.Update(use_slash_commands = True)
            await role.edit(reason = f"{ctx.author} deactivated raidmode.", permissions = permission)
            await ctx.guild.edit(reason = f"{ctx.author} activated raidmode.", verification_level = discord.VerificationLevel.medium)
        await ctx.send("Server unlocked")

    @commands.check_any(commands.has_permissions(manage_guild = True), commands.has_permissions(manage_messages = True), commands.has_permissions(manage_channels = True))
    @commands.guild_only()
    @commands.command(description = "Use to close the supplied channel(s).", aliases = ["lock-channel", "lockchan"], usage = "lockchannel <role> <channel> [channels]", hidden = False)
    async def lockchannel(self, ctx, role: discord.Role, channels : commands.Greedy[discord.TextChannel] = []): # , *, channelcheck = None
        if len(channels) < 1:
            await ctx.send(embed = discord.Embed(description = "No channels supplied.", colour = self.bot.error_colour,))
        else:
            try:
                for channel in channels:
                    await channel.set_permissions(role, reason = f"{ctx.author} locked {channel.name}", overwrite = self.raid_permission)
            except discord.Forbidden:
                await ctx.send(embed = discord.Embed(description = "The changes failed to take. Update my permissions and try again or set the overwrites manually.", colour = self.bot.error_colour,))
                #return
        await ctx.send(embed = discord.Embed(title= "Permissions for the following channels Updated successfully:", description = f"{channel.mention for channel in channels}", colour = self.bot.primary_colour))

    @commands.check_any(commands.has_permissions(manage_guild = True), commands.has_permissions(manage_messages = True), commands.has_permissions(manage_channels = True))
    @commands.guild_only()
    @commands.command(description = "Use to reeopen channel(s).", aliases = ["unlock-channel", "unlockchan"], usage = "unlockchannel <role> <channel> [channels]", hidden = False)
    async def unlockchannel(self, ctx, role: discord.Role, channels : commands.Greedy[discord.TextChannel] = []): # , *, channelcheck = None
        if len(channels) < 1:
            await ctx.send(embed = discord.Embed(description = "No channels supplied.", colour = self.bot.error_colour,))
        else:
            try:
                for channel in channels:
                    await channel.set_permissions(role, reason = f"{ctx.author} unlocked {channel.name}", overwrite = self.unraid_permission)
            except discord.Forbidden:
                await ctx.send(embed = discord.Embed(description = "The changes failed to take. Update my permissions and try again or set the overwrites manually.", colour = self.bot.error_colour,))
                #return
        await ctx.send(embed = discord.Embed(title= "Update: Channel Permissions for:", description = f"{channel.mention for channel in channels}", colour = ctx.author.colour))

    @commands.check_any(commands.has_permissions(manage_guild = True), commands.has_permissions(manage_messages = True), commands.has_permissions(manage_channels = True))
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.command(description = "Use to shutdown the preset channels during a raid.", aliases = ["lock-preset"], usage = "lockpreset", hidden = False)
    async def lockpreset(self, ctx, *, check = None):
        data = await self.bot.get_data(ctx.guild.id)
        channels = data[12]
        roles = data[11]
        if channels:
            try:
                for channel in channels:
                    channel = ctx.guild.get_channel(channel)
                    for role in roles:
                        await channel.set_permissions(ctx.guild.get_role(role), reason = "{ctx.author} locked the channel", overwrite = self.raid_permission)
            except discord.Forbidden:
                await ctx.send(embed = discord.Embed(description = "The changes failed to take. Update my permissions and try again or set the overwrites manually.", colour = self.bot.error_colour,))
                return
        await ctx.send(embed = discord.Embed(title= "Update: Channel Permissions for:", description = f"{channel.mention for channel in channels}", colour = ctx.author.colour))

    @commands.check_any(commands.has_permissions(manage_guild = True), commands.has_permissions(manage_messages = True), commands.has_permissions(manage_channels = True))
    @commands.guild_only()
    @commands.has_permissions(manage_messages = True)
    @commands.command(description = "Use to reeopen the preset(s).", aliases = ["unlock-preset"], usage = "unlockpreset", hidden = False)
    async def unlockpreset(self, ctx, *, check = None):
        data = await self.bot.get_data(ctx.guild.id)
        channels = data[12]
        roles = data[11]
        if channels:
            try:
                for channel in channels:
                    channel = ctx.guild.get_channel(channel)
                    for role in roles:
                        await channel.set_permissions(ctx.guild.get_role(role), reason = "{ctx.author} unlocked the channel.", overwrite = self.unraid_permission)
            except discord.Forbidden:
                await ctx.send(embed = discord.Embed(description = "The changes failed to take. Update my permissions and try again or set the overwrites manually.", colour = self.bot.error_colour,))
                return
        await ctx.send(embed = discord.Embed(title= "Update: Channel Permissions for:", description = f"{channel.mention for channel in channels}", colour = ctx.author.colour))

    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Sets the age in days that a user has to meet to prevent them being kicked by raidmode.", usage = "age <required age in days>", alaises = ["accage", "accountage", "account-age"])
    async def age(self, ctx, age : int):
        data = await self.bot.get_data(ctx.guild.id)
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET acc_age=$1 WHERE guild=$2", age, ctx.guild.id,)
        await ctx.send(embed = discord.Embed(colour = ctx.author.colour, title = "Update: Raidmode Required Age:", description = "{age}",))

    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Sets the bad words that aren't allowed to be said on the server.")
    async def badwords(self, ctx, *, words: str):
        print(f"\nInput: {words}")
        guild = 448405740797952010 if ctx.guild is None else ctx.guild.id
        data = await self.bot.get_data(guild)
        words = [w[1:] if w[0] == " " else w for w in words.split(",")]
        bad_words = set(words) if data[28] is None else set(data[28] + words)
        print(f"Bad Words: {bad_words}")
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET badwords=$1 WHERE guild=$2", [word for word in bad_words], guild,)
        await ctx.send(embed = discord.Embed(colour = ctx.author.colour, title= "Update: Bad Words List:", description = f"`{', '.join(data[28])}`."))

    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Sets the list of users whose messages get watched.")
    async def watch(self, ctx, users: commands.Greedy[discord.User]):
        #print(f"\nInput: {words}")
        guild = 448405740797952010 if ctx.guild is None else ctx.guild.id
        data = await self.bot.get_data(guild)
        words = [w[1:] if w[0] == " " else w for w in words.split(",")]
        bad_words = set(words) if data[28] is None else set(data[28] + words)
        print(f"Bad Words: {bad_words}")
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET badwords=$1 WHERE guild=$2", [word for word in bad_words], guild,)
        await ctx.send(embed = discord.Embed(colour = ctx.author.colour, title= "Update: Bad Words List:", description = f"`{', '.join(data[28])}`."))
    
    @checks.in_database()
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    @commands.command(description = "Set or clear the role to remove permissions from.", usage = "raidrole <role>", hidden = False)
    async def raidrole(self, ctx, role: discord.Role, *, check = None):
        if check:
            await ctx.send(embed = discord.Embed(description = f"The role is not found. Please try again.", colour = self.bot.error_colour,))
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE data SET raidrole=$1 WHERE guild=$2", role.id, ctx.guild.id,)
        await ctx.send(embed = discord.Embed(colour = ctx.author.colour, title= "Update: Raid Role", description = f"{role.mention}.", ))

    #@commands.check_any(commands.has_permissions(manage_guild = True), commands.has_permissions(manage_messages = True))
    @commands.guild_only()
    @commands.command(description = f"Lets you toggle a role as mentionable or not. Command will show the current state if no state is given.")
    async def mentionable(self, ctx, role: discord.Role, mentionable: Optional[bool]):
        print("\n\n\n")
        if mentionable is None:
            await ctx.send(f"{role.mention} is {'pingable' if role.mentionable is True else 'not pingable'}", embed = discord.Embed(description = f"{role.mention} is {'pingable' if role.mentionable is True else 'not pingable'}"))
        else:
            if mentionable is True:
                await role.edit(reason = f"{ctx.author} made {role.name} pingable.", mentionable = mentionable)
                await ctx.send(f"{role.mention} is {'pingable' if role.mentionable is True else 'not pingable'}", embed = discord.Embed(description = f"{role.mention} is {'pingable' if role.mentionable is True else 'not pingable'}"))

            else:
                await role.edit(reason = f"{ctx.author} made {role.name} not pingable.", mentionable = mentionable)
                await ctx.send(f"{role.mention} is {'pingable' if role.mentionable is True else 'not pingable'}", embed = discord.Embed(description = f"{role.mention} is {'pingable' if role.mentionable is True else 'not pingable'}"))




    
    @commands.command(description = "Lets moderators remove mass amounts of msessages.", alaises = ["purge"], usage = "clear [members] [channel] <messages>")
    @commands.bot_has_permissions(manage_messages = True)
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, targets: commands.Greedy[discord.Member], limit: int = 1, channel: discord.TextChannel = None):
        with ctx.channel.typing():
            if channel == None:
                channel_ = ctx.channel
            else:
                channel_ = channel
            with channel_.typing():
                def _check(message):
                    return not len(targets) or message.author in targets
                if 0 < limit <= 100:
                    await ctx.message.delete()
                    deleted = await channel_.purge(limit = limit, after = datetime.utcnow()-timedelta(days = 14), check = _check)
                    await ctx.send(f"Deleted **{len(deleted)}** messages.", delete_after = 5)
                    await ctx.author.send(f"You just deleted **{len(deleted)}** messages in {channel_.mention}.")
                else:
                    await ctx.send("The limit provided is not within acceptable bounds.")

    @commands.command(description = "Lets moderators mass ban members.", alaises = ["multiban", "mass-ban", "multi-ban"], usage = "massban <member> [members]. Bot prompts for [reason] and [days of messages to be deleted].")
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)
    async def massban(self, ctx, targets: commands.Greedy[discord.Member]):
        with ctx.channel.typing():
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in {"❎", "✅"}

            confirmation = await ctx.reply(f"You are about to ban `{len(targets)}` members. Do you want to add a reason for this ban?\n\n**yes** > ✅, **no** > ❎")
            await confirmation.add_reaction("✅")
            await confirmation.add_reaction("❎")

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout = 60.0, check = check)
                if str(reaction.emoji) == "✅":
                    reason_event = await self.bot.wait_for('message')
                    reason = reason_event.content
                    await confirmation.remove_reaction("✅", ctx.author)
                    await reason_event.delete(delay = 1.5)
                else:
                    reason = "Unspecified"
                    await confirmation.remove_reaction("❎", ctx.author)

            except asyncio.TimeoutError:
                confirmation.edit(content = "The time to add a reaction timed out so the defualt reason of `Unspecified` will be used.")
                reason = "Unspecified"


            await confirmation.edit(content = f"You are about to ban {len(targets)} members. Do you want to select how many days of the members messages get deleted?\n\n**yes** > ✅, **no** > ❎")
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout = 120.0, check = check)
                if str(reaction.emoji) == "✅":
                    days_event = await self.bot.wait_for('message')
                    delete_days = int(days_event.content)
                    await confirmation.remove_reaction("✅", ctx.author)
                    await days_event.delete(delay = 1.5)
                else:
                    delete_days = 1
                    await confirmation.remove_reaction("❎", ctx.author)
            except asyncio.TimeoutError:
                confirmation.edit(content = "The time to add a reaction timed out so the defualt of `1` will be used.")
                delete_days = 1

            for user in targets:
                await user.ban(reason = f"Days of deleted messages: {delete_days}\n\nBan reason:\n{reason}", delete_message_days = delete_days)
            await confirmation.edit(content = f"`{len(targets)}` members were just banned with reason `{reason}`, `{delete_days}` of messages were deleted.")
            await confirmation.clear_reactions()

            # await ctx.reply(embed = discord.Embed(title= "Member banned", description = f"{ctx.author} banned {user} for {reason}.",colour = ctx.author.color, timestamp = datetime.utcnow()), delete_after = 5)

    @checks.in_database()
    @commands.check_any(commands.has_permissions(manage_guild = True), commands.has_permissions(manage_messages = True), commands.has_permissions(manage_channels = True))
    @commands.guild_only()
    @commands.command(description = "View the moderation cog configuration for the current server.", usage = "modconfig")
    async def modconfig(self, ctx):
        data = await self.bot.get_data(ctx.guild.id)
        raidmode_log = ctx.guild.get_channel(data[16])
        join_leave_log = ctx.guild.get_channel(data[19])

        raid_roles = []
        for role in data[11]:
            if role == -1:
                raid_roles.append("@here")
            elif role == ctx.guild.default_role.id:
                raid_roles.append("@everyone")
            else:
                raid_roles.append(f"<@&{role}>")
        locked_channels = []
        for channel in data[12]:
            locked_channels.append(f"<#{channel}>")

        embed = discord.Embed(title= "Moderation Configuration", colour = self.bot.primary_colour)
        embed.add_field(name = "Prefix", value = f"`{self.bot.tools.get_guild_prefix(self.bot, ctx.guild)}`")
        embed.add_field(name = "Raidmode", value = "Enabled" if data[14] is True else "Disabled")
        embed.add_field(name = "Required Account Age", value = f"**{data[15]}** days" )
        embed.add_field(name = "Raidmode log", value = f"*Not set*" if raidmode_log is None else f"<#{raidmode_log.id}>", inline = True)
        embed.add_field(name = "Join/Leave log", value = f"*Not set*" if join_leave_log is None else f"<#{join_leave_log.id}>", inline = True)
        embed.add_field(name = "Locked Channels", value = "*Not set*" if len(locked_channels) == 0 else " ".join(locked_channels), inline = False)
        embed.add_field(name = "Locked Roles", value = "*Not set*" if len(raid_roles) == 0 else " ".join(raid_roles), inline = False)
        await ctx.send(embed = embed)

    @checks.in_database()
    @commands.check_any(commands.has_permissions(manage_guild = True), commands.has_permissions(manage_messages = True), commands.has_permissions(manage_channels = True))
    @commands.guild_only()
    @commands.command(description = "View the entire configuration for the current server.", usage = "viewconfig")
    async def viewconfig(self, ctx):
        data = await self.bot.get_data(ctx.guild.id)
        category = ctx.guild.get_channel(data[2]) # Configuration - Modmail cog
        logging = ctx.guild.get_channel(data[4]) # Configuration - Modmail cog
        raidmode_log = ctx.guild.get_channel(data[16]) # Moderation cog
        join_leave_log = ctx.guild.get_channel(data[18]) # Moderation cog
        counting_channel = ctx.guild.get_channel(data[22]) # Counting cog
        deleted_messages = ctx.guild.get_channel(data[23])
        edited_messages = ctx.guild.get_channel(data[24])
        suggestions = ctx.guild.get_channel(data[25])
        starboard = ctx.guild.get_channel(data[27])

        # Configuration - Modmail cog
        access_roles = []
        for role in data[3]:
            access_roles.append(f"<@&{role}>")
        ping_roles = []
        for role in data[8]:
            if role == -1:
                ping_roles.append("@here")
            elif role == ctx.guild.default_role.id:
                ping_roles.append("@everyone")
            else:
                ping_roles.append(f"<@&{role}>")
        welcome = data[5]
        if welcome and len(welcome) > 1000:
            welcome = welcome[:997] + "..."
        goodbye = data[6]
        if goodbye and len(goodbye) > 1000:
            goodbye = goodbye[:997] + "..."
        blacklist = []
        for user in data[9]:
            blacklist.append(f"<@{user}>")
        # Moderation cog
        raid_roles = []
        for role in data[11]:
            if role == -1:
                raid_roles.append("@here")
            elif role == ctx.guild.default_role.id:
                raid_roles.append("@everyone")
            else:
                raid_roles.append(f"<@&{role}>")
        locked_channels = []
        for channel in data[12]:
            locked_channels.append(f"<#{channel}>")

        # Counting Cog
        mistakes_roles = []
        for role in data[17]:
            if role == -1:
                mistakes_roles.append("@here")
            elif role == ctx.guild.default_role.id:
                mistakes_roles.append("@everyone")
            else:
                mistakes_roles.append(f"<@&{role}>")

        embed = discord.Embed(title= "Server Configuration", description = f"""
        **Mail Greeting Message:**\n{'*Not set*' if welcome is None else welcome}\n\n
        **Mail Closing Message:**\n{'*Not set*' if goodbye is None else goodbye}""", colour = ctx.author.colour)
        #embed.set_author(name = f"Raidmode: {'Enabled' if data[14] is True else 'Disabled'} | Advanced Logging: {'Enabled' if data[7] is True else 'Disabled'} | Anonymous Messaging: {'Enabled' if data[10] is True else 'Disabled'}")
        embed.add_field(name = "Prefix", value = f"`{self.bot.tools.get_guild_prefix(self.bot, ctx.guild)}`", inline = False)
        embed.add_field(name = "Raidmode", value = "Enabled" if data[14] is True else "Disabled", inline = True)
        embed.add_field(name = "Advanced Logging", value="Enabled" if data[7] is True else "Disabled", inline = True)
        embed.add_field(name = "Anonymous Messaging", value="Enabled" if data[10] is True else "Disabled", inline = True)

        embed.add_field(name = "Required Account Age", value = f"**{data[15]}** days", inline = True)
        embed.add_field(name = "Current Number", value = data[13], inline = True)
        embed.add_field(name = "Next Number", value = f"{data[13] + 1}", inline = True)

        embed.add_field(name = "Mail Category", value ="*Not set*" if category is None else category.name, inline = True)
        embed.add_field(name = "Mail Logging", value="*Not set*" if logging is None else f"<#{logging.id}>", inline = True)
        embed.add_field(name = "Starboard", value = f"*Not set*" if starboard is None else f"<#{starboard.id}>", inline = True)
        embed.add_field(name = "Suggestions", value = f"*Not set*" if suggestions is None else f"<#{suggestions.id}>", inline = True)
        embed.add_field(name="Counting Channel", value = "*Not set*" if counting_channel is None else f"<#{counting_channel.id}>", inline = True)
        embed.add_field(name = "Join/Leave log", value = f"*Not set*" if join_leave_log is None else f"<#{join_leave_log.id}>", inline = True)
        embed.add_field(name = "Raidmode log", value = f"*Not set*" if raidmode_log is None else f"<#{raidmode_log.id}>", inline = True)
        embed.add_field(name = "Locked Channels", value = "*Not set*" if len(locked_channels) == 0 else " ".join(locked_channels), inline = True)

        embed.add_field(name = "Mail Access Roles", value = "*Not set*" if len(access_roles) == 0 else " ".join(access_roles), inline = False)
        embed.add_field(name = "Mail Ping Roles", value = "*Not set*" if len(ping_roles) == 0 else " ".join(ping_roles), inline = True)
        embed.add_field(name = "Counting Mistakes Roles", value = "*Not set*" if len(mistakes_roles) == 0 else " ".join(mistakes_roles), inline = True)
        embed.add_field(name = "Locked Roles", value = "*Not set*" if len(raid_roles) == 0 else " ".join(raid_roles), inline = True)
        
        #embed.add_field(name = "Mail Greeting Message", value="*Not set*" if welcome is None else welcome, inline = False)
        #embed.add_field(name = "Mail Closing message", value="*Not set*" if goodbye is None else goodbye, inline = False)


        #second = discord.Embed(title= "Server Configuration", colour = ctx.author.colour)
        #second.add_field(name = "Prefix", value = f"`{self.bot.tools.get_guild_prefix(self.bot, ctx.guild)}`", inline = True)
        #second.add_field(name = "Mail Category", value ="*Not set*" if category is None else category.name, inline = True)
        #second.add_field(name = "Mail Logging", value="*Not set*" if logging is None else f"<#{logging.id}>", inline = True)
        #second.add_field(name = "Advanced Logging", value="Enabled" if data[7] is True else "Disabled", inline = True)
        #second.add_field(name = "Anonymous Messaging", value="Enabled" if data[10] is True else "Disabled", inline = True)
        #second.add_field(name = "Mail Access Roles", value = "*Not set*" if len(access_roles) == 0 else " ".join(access_roles), inline = False)
        #second.add_field(name = "New Ping Roles", value = "*Not set*" if len(ping_roles) == 0 else " ".join(ping_roles), inline = False)
        #second.add_field(name = "Mail Greeting Message", value="*Not set*" if welcome is None else welcome, inline = False)
        #second.add_field(name = "Mail Closing message", value="*Not set*" if goodbye is None else goodbye, inline = False)

        #second.add_field(name = "Raidmode", value = "Enabled" if data[14] is True else "Disabled", inline = True)
        #second.add_field(name = "Raidmode log", value = f"*Not set*" if raidmode_log is None else f"<#{raidmode_log.id}>", inline = True)
        #second.add_field(name = "Required Account Age", value = f"**{data[15]}** days", inline = True)
        #second.add_field(name = "Locked Channels", value = "*Not set*" if len(locked_channels) == 0 else " ".join(locked_channels), inline = False)
        #second.add_field(name = "Locked Roles", value = "*Not set*" if len(raid_roles) == 0 else " ".join(raid_roles), inline = False)

        #second.add_field(name = "Current Number", value = data[13], inline = True)
        #second.add_field(name = "Next Number", value = f"{data[13] + 1}", inline = True)
        #second.add_field(name="Counting Channel", value = "*Not set*" if len(counting_channel) == 0 else " ".join(counting_channel), inline = False)
        #second.add_field(name = "Counting Mistakes Roles", value = "*Not set*" if len(mistakes_roles) == 0 else " ".join(mistakes_roles), inline = False)
        
        await ctx.send(embed = embed)
        #await ctx.send(embed = second)

    @commands.has_permissions(administrator = True)
    @commands.command()
    async def modlogs(self, ctx):
        snowyjaguar = self.bot.get_user(self.bot.config.owner)
        #key_words = ["WARN", "MUTE", "UNMUTE", "KICK", "BAN", "UNBAN"] # Add in Captilised versions of each word to account for the Dyno logs
        checked_logs = []
        case_count = 0
        last_checked = 0
        moderation = await self.bot.fetch_channel(885569667861717042)
        clifford_log = await self.bot.fetch_channel(500768218257031168)
        await ctx.reply(f"You used `{ctx.command.name}`, I have been able to fetch {moderation.mention} and {clifford_log.mention}")
         # Field One: User who was moderated *, Field Two: Moderator who performed the moderation *, Field Three: Reason for moderation, Field Four: Duration of moderation

        with moderation.typing():
            messages = await clifford_log.history(oldest_first = True, limit = None,).flatten() # 10000, after = last_checked
            for message in messages[0:]: # Making bot search history chronologically
                if all([
                    message.id not in checked_logs, 
                    message.author.id == 776782769312628746, 
                    len(message.embeds) > 0, 
                ]):
                    action = [word for word in self.bot.config.key_words if word in message.embeds[0].title]
                    if len(action) > 0:
                    #if action := [word for word in self.bot.config.key_words if word in message.embeds[0].title]:
                        embed = discord.Embed(title = f"{action[0]} | Case {case_count}", colour = self.bot.config.error_colour, timestamp = message.Embed.timestamp)
                        embed.set_author(name = f"{message.embeds[0].fields[0].value} | {message.embeds[0].fields[0].value.id}", icon_url = message.embeds[0].fields[0].value.avatar_url)
                        embed.set_footer(text = f"{message.embeds[0].fields[1].value} | {message.embeds[0].fields[1].value.id}", icon_url = {message.embeds[0].fields[1].value.avatar_url})
                        embed.add_field(name = "Offender", value = message.embeds[0].fields[0].value, inline = True)
                        embed.add_field(name = "Moderator", value = message.embeds[0].fields[1].value, inline = True)
                        if message.embeds[0].fields[3]:
                            embed.add_field(name = "Duration", value = message.embeds[0].fields[3].value)
                        if message.embeds[0].fields[2]:
                            embed.add_field(name = "Reason", value = message.embeds[0].fields[2].value)
                        checked_logs.append(message.id)
                        case_count += 1
                        last_checked = message.Embed.timestamp

                        await moderation.send(embed = embed)
            await snowyjaguar.send(f"`{len(messages)}` messages were checked in {clifford_log.mention}, `{case_count}` logs were logged in {moderation.mention}, messages: {checked_logs}")
    
"""
    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await self.bot.get_data(member.guild.id)
        log = self.bot.get_channel(id = data[16])
        if data[14] == True and member.guild.id == data[0]:
            acc_age = datetime.utcnow() - member.created_at
            if acc_age < timedelta(days = data[15]):
                try:
                    embed = discord.Embed(title= "Member Kicked!", description = f'{member.name}#{member.discriminator} account is **{acc_age.days}** days old and so the member was kicked by raidmode.')
                    await member.send(f"This server has raidmode **active** and requires users have a account that is older than **{data[15]}** days old. As your account is less than the servers threshold you have been kicked.")
                    await member.kick(reason = f"Raidmode enabled: {member.name}#{member.discriminator}'s account was deemeed too new by your raidmode configuration. The required age is {data[15]} days old and this users account is{acc_age.days} days old. You can check the current required age with the modconfig command.")
                    await log.send(embed = embed)

                except discord.HTTPException:
                    embed = discord.Embed(title= "Member Kicked!", description = f'{member.name}#{member.discriminator} account is {acc_age.days} days old and so member was kicked by raidmode')
                    embed.add_field(name = "Additional ", value = f"I could not message this member to inform them of the reason they were kicked. This is normally becuase they have their direct messages turned off.")
                    await log.send(embed = embed)
                    await member.kick(reason = f"Raidmode enabled: The users account was deemeed too new by the raidmode configuration. The required age is {data[15]} days old and this users account is{acc_age.days} days old. You can check the current required age with the `modconfig` command.")
"""


"""
    @commands.command(description="filler 3.",
    usage="filler 4")
    async def time(ctx, member : discord.Member):
        time = member.created_at
        age = datetime.datetime.now()
        acc_age = age - time
        acc = acc_age.days

        if acc_age.days < 1:
            acc1 = acc_age.days*86400
            await ctx.send(f"{member.name}'s account is {acc1} seconds!")
            return
        else:
            await ctx.send(f"{member.name}'s account is {acc} days old!")
"""

"""
    @commands.command(description = " Kicks a member from a voice channel")
    async def vckick(ctx, member : discord.Member, channel : VoiceChannel = None):
        if member.voice:
            await member.move_to(None)
            embed = discord.Embed(description= f" {member.mention} has been kicked from the voice channel ", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description= f" {member.mention} is currently not in a Voice Channel ", color=discord.Color.red())
            await ctx.send(embed=embed)
"""
""" 
    @checks.in_database()
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command(description = "Manually verify user using the first listed role in the raidrole command.", usage = "verify [user]", hidden=False)
    async def verify(self, ctx, member: discord.Member, *, check=None):
        data = await self.bot.get_data(ctx.guild.id)
        roles = data[11]
        if check:
            await ctx.send(embed = discord.Embed(description = f"The user(s) are not found. Please try again.", colour = self.bot.error_colour,))
            return
        if member:
            try:
                user = member.id
                role = ctx.guild.get_role(roles[0])
                await member.add_roles(role)
            except IndexError:
                await ctx.send(embed = discord.Embed(description = f"The role is not found. Please try again.", colour = self.bot.error_colour,))
                return
        await ctx.send(embed = discord.Embed(description = "The role is Updated successfully.", colour = self.bot.primary_colour)) 
"""

""" 
    @checks.in_database()
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command(description = "Manually unverify user using the first listed role in the raidrole command.", usage = "verify [user]", hidden=False)
    async def unverify(self, ctx, member: discord.Member, *, check=None):
        data = await self.bot.get_data(ctx.guild.id)
        roles = data[11]
        if check:
            await ctx.send(embed=discord.Embed(description = f"The user(s) are not found. Please try again.", colour = self.bot.error_colour,))
            return
        if member:
            try:
                user = member.id
                role = ctx.guild.get_role(roles[0])
                await member.remove_roles(role)
            except IndexError:
                await ctx.send(embed = discord.Embed(description = f"The role is not found. Please try again.", colour = self.bot.error_colour,))
                return
        await ctx.send(embed = discord.Embed(description = "The role is Updated successfully.", colour = self.bot.primary_colour)) 
"""
    

def setup(bot):
    bot.add_cog(Moderation(bot))
