import logging
import discord
import asyncio

from utils import checks
from discord.ext import commands
from discord.utils import get
from discord_slash import SlashCommand, SlashContext, cog_ext
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import ButtonStyle
from collections import OrderedDict, deque, Counter
from typing import Optional, Union

log = logging.getLogger(__name__)

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def parent(self, ctx):
        group_commands = []
        if isinstance(ctx, commands.Context):
            for command in ctx.command.commands:
                command_string = f"`{ctx.prefix + command.name}`"
                group_commands.append(command_string)
            await ctx.reply(embed = discord.Embed(title = f"Commands in `{ctx.command.name}`", description = ", ".join(group_commands)))
        elif isinstance(ctx, SlashContext):
            #for command in ctx.command.commands:
                #command_string = f"`{ctx.prefix + command.name}`"
                #group_commands.append(command_string)
            #await ctx.reply(embed = discord.Embed(title = f"Commands in `{ctx.command.name}`", description = ", ".join(group_commands)))
            await ctx.reply("Completed `isistance` check on slash command context", hidden = True)
        else:
            await ctx.reply("Uhhh, what did you pass to me?", hidden = True)
    

    async def timestamps(self, member, embed, avatar):
        embed.add_field(name = "Joined Server:", value = f"<t:{int(member.joined_at.timestamp())}:R>", inline = True)
        if avatar == True:
            embed.add_field(name = "Avatar", value = f"[PNG]({member.avatar_url_as(static_format='png')})", inline = True)
        embed.add_field(name = "Joined Discord:", value = f"<t:{int(member.created_at.timestamp())}:R>", inline = True)
    
    async def emoji_counter(self, guild):
        emoji_stats = Counter()
        for emoji in guild.emojis:
            if emoji.animated:
                emoji_stats['animated'] += 1
                emoji_stats['animated_disabled'] += not emoji.available
            else:
                emoji_stats['regular'] += 1
                emoji_stats['disabled'] += not emoji.available

            fmt = f'Regular: {emoji_stats["regular"]}/{guild.emoji_limit} |     Animated: {emoji_stats["animated"]}/{guild.emoji_limit}'\

            if emoji_stats['disabled'] or emoji_stats['animated_disabled']:
                fmt = f'{fmt} Disabled: {emoji_stats["disabled"]} regular, {emoji_stats["animated_disabled"]} animated\n'

            fmt = f'{fmt} | Total Emojis: {len(guild.emojis)}/{guild.emoji_limit*2}'

        return fmt

    @commands.group(name = "user", aliases = ["member"], invoke_without_command = True, case_insensitive = True,)
    async def user_group(self, ctx):
       await self.parent(ctx)
        
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    @user_group.command(description = "Show a member's permission in a channel when specified.", usage = "[member] [channel]", aliases = ["perms"])
    async def permissions(self, ctx, member: discord.Member = None, channel: Union[discord.TextChannel, discord.VoiceChannel, discord.StageChannel, discord.CategoryChannel] = None):
        channel = channel or ctx.channel
        member = member or ctx.author
        permissions = channel.permissions_for(member)
        embed = discord.Embed(title="Permission Information", colour = member.colour)
        embed.add_field(name="User", value=str(member), inline=False)
        embed.add_field(name = "Allowed", value = ", ".join([self.bot.tools.perm_format(name) for name, value in permissions if value]), inline = False)
        embed.add_field(name = "Denied", value=", ".join([self.bot.tools.perm_format(name) for name, value in permissions if not value]), inline = False)
        await ctx.reply(embed=embed)

    @user_group.command(name = "info", description = "Show some information about yourself or the member specified.", usage = "[member]", aliases = ["whois", "ui"])
    async def zinfo(self, ctx, member: discord.Member = None):
        member = ctx.author if member is None else member
        roles = [f"{role.mention}" for role in member.roles]
        has_key = [perm for perm in self.bot.config.key_perms if getattr(member.guild_permissions, perm)]
        if len(has_key) == 0:
            has_key.append('No permissions')
        member_status = "No status" if member.activity is None else member.activity.name
        if len(roles) == 0:
            roles.append("No roles")

        embed = discord.Embed(title = f"{member.name}#{member.discriminator}", description = f"Status: **{member.status}**\n*{member_status}*", colour = member.colour)
        embed.set_author(name = f"{member.id}", icon_url = member.avatar_url)
        embed.set_thumbnail(url = member.avatar_url)
        await self.timestamps(member, embed, True)
        embed.add_field(name = f"Roles: {len(roles)}",value = f"{len(roles)} roles" if len(" ".join(roles)) > 1000 else " ".join(roles), inline = False)
        embed.add_field(name =f'Key permissions', value = ", ".join(has_key).replace("_"," ").title(), inline = False)
        await ctx.reply(embed = embed)

    @user_group.command(description = "Show when yourself or the member specified joined the {ctx.guild.name} and Discord.", usage = "[member]", aliases = ["dates", "created", "j"])
    async def joined(self, ctx, member: discord.Member = None):
        member = ctx.author if member is None else member
        embed = discord.Embed(title = f"{member}", colour = member.colour)
        embed.set_author(name = f"{member.id}", icon_url = member.avatar_url)
        embed.set_thumbnail(url = member.avatar_url)
        await self.timestamps(member, embed, False)
        await ctx.reply(embed = embed)

    @user_group.command(description = "Show a users avatar.", usage = "[member]", aliases = ["av"])
    async def avatar(self, ctx, member: discord.Member = None):
        member = ctx.author if member is None else member
        embed = discord.Embed(title = f"{member.name}#{member.discriminator}'s Avatar", colour = member.colour)
        embed.add_field(name = "PNG", value = f"[Link]({member.avatar_url_as(static_format='png')})", inline = True)
        embed.add_field(name = "JPG", value = f"[Link]({member.avatar_url_as(static_format='jpg')})", inline = True)
        embed.add_field(name = "WebP", value = f"[Link]({member.avatar_url_as(static_format='webp')})", inline = True)
        embed.set_image(url = member.avatar_url)
        await ctx.reply(embed = embed)

    @user_group.command(description = "Show the roles of the member specified or yourself.", usage = "[member]",)
    async def roles(self, ctx, member: discord.Member = None):
        member = ctx.author if member is None else member
        roles = [f"<@&{role.id}>" for role in member.roles]
        if len(roles) == 0:
            roles.append("No roles")
        await ctx.reply(embed = discord.Embed(title = f"Roles for {member}: {len(roles)}" if len(" ".join(roles)) > 1000 else " ".join(roles), description = f" ".join(roles)))
    
    @user_group.command(description = "Show the status of a member or of yourself.", usage = "[member]", aliases = ["us"])
    async def status(self, ctx, *, member: discord.Member = None):
            member = ctx.author if member is None else member
            member_status = "No status" if member.activity is None else member.activity.name
            embed = discord.Embed(title = f"{member}", description = f"Status: **{member.status}**\n*{member_status}*", colour = member.colour)
            embed.set_author(name = f"{member.id}", icon_url = member.avatar_url)
            embed.set_thumbnail(url = member.avatar_url)
            await ctx.reply(embed = embed, mention_author = True)



    @commands.group(name = "role", invoke_without_command = True, case_insensitive = True, aliases = ["rank"])
    async def role_group(self, ctx):
        await self.parent(ctx)

    @role_group.command(description = "Show information about the given role.", usage = "<role>", aliases = ["whatis", "ri"])
    async def info(self, ctx, role : discord.Role):
        has_perm = [perm for perm in self.bot.config.role_perms if getattr(role.permissions, perm)]

        embed = discord.Embed(title = f"{role.name}", description = f"{role.mention} was created <t:{int(role.created_at.timestamp())}:R>", color = role.colour)
        embed.set_author(name = f"ID: {role.id}")
        embed.add_field(name = "Members in role:", value = len(role.members), inline = True)
        embed.add_field(name = "Position", value = role.position, inline = True)
        embed.add_field(name = "Colour:", value = role.colour, inline = True)
        embed.add_field(name = "Hoisted:", value = role.hoist, inline = True)
        embed.add_field(name = "Mentionable:", value = role.mentionable, inline = True)
        embed.add_field(name = "Intergration:", value = role.managed, inline = True)   
        embed.add_field(name = f'Permissions', value = ", ".join(has_perm).replace("_"," ").title(), inline = False)
        await ctx.reply(embed = embed)

    @role_group.command(description = "Show the members of the role specified.", usage = "[role]",)
    async def members(self, ctx, role: discord.Role):
        members = [f"{member.mention}, " for member in role.members]

        if len(members) == 0: members.append("No members")
        await ctx.reply(embed = discord.Embed(title = f"{len(role.members)} Members in `{role}`", description = f" ".join(members)))

    @role_group.command(description = "Show the members of the role specified.", usage = "[role]", aliases = ["perms"])
    async def permissions(self, ctx, role: discord.Role):
        has_perm = [perm[0] for perm in role.permissions if perm[1]]
        if len(has_perm) == 0:
            has_perm.append('No permissions')
        await ctx.reply(embed = discord.Embed(title = f"Permissions for `{role}`", description = f", ".join(has_perm).replace("_"," ").title()))

    @commands.group(name = "channel", aliases = ["chan", "room", "chat"], invoke_without_command = True, case_insensitive = True,)
    async def channel_group(self, ctx):
        await self.parent(ctx)

    @channel_group.command(description = "Show information about the given channel.", usage = "<channel>", aliases = ["ci"])
    async def info(self, ctx, channel : Union[discord.TextChannel, discord.VoiceChannel, discord.StageChannel, discord.CategoryChannel]):
        with ctx.channel.typing():
            embed = discord.Embed(title = f"{channel.name}", description = f"{channel.mention} was created <t:{int(channel.created_at.timestamp())}:R>", colour = ctx.author.colour)
            embed.set_author(name = f"ID: {channel.id}")
            if channel.category == None:
                embed.add_field(name = "Category", value = "None", inline = True)
            else:
                embed.set_footer(text = f"Category ID: {channel.category.id}")
                embed.add_field(name = "Category", value = channel.category, inline = True)
            embed.add_field(name = "Position", value = channel.position, inline = True)
            if channel in ctx.guild.text_channels:
                embed.add_field(name = "Slowmode Delay", value = channel.slowmode_delay, inline = True)
                embed.add_field(name = "Topic", value = channel.topic, inline = False)
                embed.add_field(name = "Announcement:", value = channel.is_news(), inline = True)

            elif channel in ctx.guild.categories:
                embed.add_field(name = "Channels", value = len(channel.channels), inline = True)
                embed.add_field(name = "Text", value = len(channel.text_channels), inline = True)
                embed.add_field(name = "Voice", value = len(channel.voice_channels), inline = True)
                embed.add_field(name = "Stage", value = len(channel.stage_channels), inline = True)

            elif channel in ctx.guild.voice_channels or channel in ctx.guild.stage_channels:
                embed.add_field(name = "Bitrate", value = channel.bitrate, inline = True)
                embed.add_field(name = "Region", value = "Automatic" if channel.rtc_region == None else channel.rtc_region, inline = True)
                embed.add_field(name = "user Limit", value = channel.user_limit, inline = True)
                embed.add_field(name = "Voice states", value = channel.voice_states, inline = True)
                if channel in ctx.guild.stage_channels:
                    embed.add_field(name = "Topic", value = channel.topic, inline = False)
                    embed.add_field(name = "Requesting to speak", value = len(channel.requesting_to_speak), inline = True)
            else:
                print("Channel info else.")

            embed.add_field(name = "Type:", value = channel.type, inline = True)
            embed.add_field(name = "Synced:", value = channel.permissions_synced, inline = True)
            await ctx.reply(embed = embed)

    @channel_group.command(description = "Check a channels topic.", usage = "[channel]")
    async def topic(self, ctx, channel : discord.TextChannel = None):
        channel = channel or ctx.channel
        await ctx.reply(embed = discord.Embed(title = channel.name, description = channel.topic, colour = ctx.author.colour))

    @commands.group(name = "emoji", invoke_without_command = True, case_insensitive = True,)
    async def emoji_group(self, ctx):
        await self.parent(ctx)


    @emoji_group.command(description = "Get Information about a emoji.", usage = "<emoji>", aliases = ["emo", "stats"])
    async def info(self, ctx, emoji : Union[discord.Emoji, discord.PartialEmoji]):
        embed = discord.Embed(title = f"{emoji.name}", description = f"Created <t:{int(emoji.created_at.timestamp())}:R>", colour = ctx.author.colour)
        embed.set_author(name = f"{emoji.id}", icon_url = emoji.url)
        embed.set_thumbnail(url = emoji.url)
        embed.add_field(name = "Raw Format", value = f"`<a:{emoji.name}:{emoji.id}>`" if emoji.animated == True else f"`<:{emoji.name}:{emoji.id}>`")
        await ctx.reply(embed = embed)

    @emoji_group.command(description = "Clone emojis!", usage = "<emoji>", aliases = ["add", "copy"])
    @commands.has_permissions(manage_emojis = True)
    @commands.bot_has_permissions(manage_emojis = True)
    async def clone(self, ctx, emoji: Union[discord.PartialEmoji, discord.Emoji]= None):
        message = await ctx.reply(f"Cloning please wait... <:{emoji.name}:{emoji.id}>['loading']")
        if emoji not in ctx.guild.emojis:
            if isinstance(emoji, discord.PartialEmoji):
                emo = await ctx.guild.create_custom_emoji(name=emoji.name, image=await emoji.url.read(), reason=f"{ctx.command.name} command used by {ctx.author} ({ctx.author.id})")
            await message.edit(content=f"Emoji <:{emo.name}:{emo.id}> was added!")
        else:
            await message.edit(content=f"Emoji <:{emoji.name}:{emoji.id}> is already a emoji in this server")

    @emoji_group.command(description = "Enlarge an emoji.", usage = "<emoji>")
    async def enlarge(self, ctx, emoji: Union[discord.Emoji, discord.PartialEmoji, str] = None):
        await ctx.reply(emoji.url)

    @cog_ext.cog_subcommand(base = "user", name = "info", description = "Show some information about yourself or the member specified.", options = [create_option(name = "member", description = "If no member is giving it will show your information.", option_type = 6, required = False,)])
    async def _userinfo(self, ctx: SlashContext, member: discord.Member = None):
        #await self.parent(ctx)
        member = ctx.author if member is None else member
        roles = [f"<@&{role.id}>" for role in member.roles]
        key_perms = ["administrator", "manage_guild", "manage_roles", "manage_channels", "manage_messages", "manage_webhooks", "manage_nicknames", "manage_emojis", "kick_members", "mention_everyone"]
        has_key = [perm for perm in key_perms if getattr(member.guild_permissions, perm)]
        if len(has_key) == 0:
            has_key.append('No permissions')
        member_status = "No status" if member.activity is None else member.activity.name
        if len(roles) == 0:
            roles.append("No roles")

        embed = discord.Embed(title = f"{member.name}#{member.discriminator}", description = f"Status: **{member.status}**\n*{member_status}*", colour = member.colour)
        embed.set_author(name = f"{member.id}", icon_url = member.avatar_url)
        embed.set_thumbnail(url = member.avatar_url)
        await self.timestamps(member, embed, True)
        embed.add_field(name = f"Roles: {len(roles)}",value = f"{len(roles)} roles" if len(" ".join(roles)) > 1000 else " ".join(roles), inline = False)
        embed.add_field(name =f'Key permissions', value = ", ".join(has_key).replace("_"," ").title(), inline = False)
        await ctx.reply(embed = embed)

    

    @cog_ext.cog_subcommand(base = "user", name = "joined", description = "Show when yourself or the member specified joined the {ctx.guild.name} and Discord.", options = [create_option(name = "member", description = "If no member is giving it will show your information.", option_type = 6, required = False,)])
    async def _joined(self, ctx: SlashContext, member: discord.Member = None):
        member = ctx.author if member is None else member
        embed = discord.Embed(title = f"{member}", colour = member.colour)
        embed.set_author(name = f"{member.id}", icon_url = member.avatar_url)
        embed.set_thumbnail(url = member.avatar_url)
        await self.timestamps(member, embed, True)
        await ctx.reply(embed = embed, hidden = True)
    
    @cog_ext.cog_subcommand(base = "user", name = "avatar", description = "Show a users avatar.", options = [create_option(name = "member", description = "If no member is given it will show your information.", option_type = 6, required = False,)])
    async def _avatar(self, ctx: SlashContext, member: discord.Member = None):
        member = ctx.author if member is None else member
        embed = discord.Embed(title = f"{member}'s Avatar", colour = member.colour)
        embed.add_field(name = "PNG", value = f"[Link]({member.avatar_url_as(static_format='png')})", inline = True)
        embed.add_field(name = "JPG", value = f"[Link]({member.avatar_url_as(static_format='jpg')})", inline = True)
        embed.add_field(name = "WebP", value = f"[Link]({member.avatar_url_as(static_format='webp')})", inline = True)
        #embed.add_field(name = "GIF", value = f"[Link]({member.avatar_url_as(static_format='gif')})", inline = True)
        embed.set_image(url = member.avatar_url)
        await ctx.reply(embed = embed)

    @commands.guild_only()
    @commands.command(description = "Get some information about this server.", usage = "serverinfo", aliases = ["guildinfo", "serverstats", "guildstats", "server-info", "guild-info", "server-stats", "guild-stats", "si"],)
    async def serverinfo(self, ctx, guild: Optional[discord.Guild]):
        with ctx.channel.typing():
            guild = guild or ctx.guild
            embed = discord.Embed(title = f"{guild.name}", description = f"Server created <t:{int(guild.created_at.timestamp())}:R>", colour = ctx.author.colour)
            embed.set_author(name = f"ID: {guild.id}", icon_url = guild.icon_url)
            embed.set_thumbnail(url = guild.banner_url if guild.banner_url else guild.icon_url)
            # Cluster related Information for if/when the bot gets clustered.
            if guild:
                embed.set_footer(text = f"Cluster: {self.bot.cluster} | Shard: {guild.shard_id + 1}")
            else:
                embed.set_footer(text = f"Cluster: {self.bot.cluster}/{self.bot.cluster_count} | Shard: {self.shard_count}")
            embed.add_field(name = "Owner", value = f"{guild.owner.name}#{guild.owner.discriminator}" if guild.owner_id else "Unknown")
            embed.add_field(name = "Icon", value = f"[Link]({guild.icon_url_as(static_format='png')})" if guild.icon else "*Not set*")
            embed.add_field(name = "Banner", value = f"[Link]({guild.banner_url})" if guild.banner else "*Not set*")

            embed.add_field(name = "Emotes", value = await self.emoji_counter(guild), inline = False)
            embed.add_field(name = "Members", value = f"{guild.member_count}/{guild.max_members}", inline = True)
            embed.add_field(name = "Channels", value = len(guild.channels), inline = True)
            embed.add_field(name = "Roles", value = len(guild.roles), inline = True)
            embed.add_field(name = "Server Boosts", value = (guild.premium_subscription_count), inline = True)
            embed.add_field(name = "Server Boost Level", value = (guild.premium_tier), inline = True)
            await ctx.reply(embed = embed)

    @cog_ext.cog_slash(name = "server-info", description = "Get some information about this server.")
    async def _serverinfo(self, ctx: SlashContext, guild: discord.Guild = None):
        guild = guild or ctx.guild
        embed = discord.Embed(title = f"{guild.name}", description = f"Server created <t:{int(guild.created_at.timestamp())}:R>", colour = ctx.author.colour)
        embed.set_author(name = f"ID: {guild.id}", icon_url = guild.icon_url)
        embed.set_thumbnail(url = guild.banner_url if guild.banner_url else guild.icon_url)
        # Cluster related Information for if/when the bot gets clustered.
        if guild:
            embed.set_footer(text = f"Cluster: {self.bot.cluster} | Shard: {guild.shard_id + 1}")
        else:
            embed.set_footer(text = f"Cluster: {self.bot.cluster}/{self.bot.cluster_count} | Shard: {self.shard_count}")
        embed.add_field(name = "Owner", value = f"{guild.owner.name}#{guild.owner.discriminator}" if guild.owner_id else "Unknown")
        embed.add_field(name = "Icon", value = f"[Link]({guild.icon_url_as(static_format='png')})" if guild.icon else "*Not set*")
        embed.add_field(name = "Banner", value = f"[Link]({guild.banner_url})" if guild.banner else "*Not set*")

        embed.add_field(name = "Emotes", value = await self.emoji_counter(guild), inline = False)
        embed.add_field(name = "Members", value = f"{guild.member_count}/{guild.max_members}", inline = True)
        embed.add_field(name = "Channels", value = len(guild.channels), inline = True)
        embed.add_field(name = "Roles", value = len(guild.roles), inline = True)
        embed.add_field(name = "Server Boosts", value = (guild.premium_subscription_count), inline = True)
        embed.add_field(name = "Server Boost Level", value = (guild.premium_tier), inline = True)
        await ctx.reply(embed = embed)

    @cog_ext.cog_subcommand(base = "role", name = "info", description = "Show information about the given role.", options = [create_option(name = "role", description = "Role argument is required.", option_type = 8, required = True,)])
    async def _roleinfo(self, ctx: SlashContext, role: discord.Role):
            role_perms = ['administrator', 'manage_guild', 'manage_webhooks', 'manage_channels', 'manage_roles', 'manage_emojis', 'manage_messages', 'manage_nicknames', 'view_audit_log', 'view_guild_insights', 'kick_members', 'ban_members', 'move_members', 'deafen_members', 'mute_members', 'read_messages', 'send_messages', 'send_tts_messages', 'embed_links', 'attach_files', 'read_message_history', 'add_reactions', 'external_emojis', 'connect', 'speak', 'priority_speaker', 'use_voice_activation', 'stream', 'create_instant_invite', 'change_nickname', 'mention_everyone']
            has_perm = [perm for perm in role_perms if getattr(role.permissions, perm)]

            embed = discord.Embed(title = f"{role.name}", description = f"{role.mention} was created <t:{int(role.created_at.timestamp())}:R>", color = role.colour)
            embed.set_author(name = f"ID: {role.id}")
            embed.add_field(name = "Members in role:", value = len(role.members), inline = True)
            embed.add_field(name = "Position", value = role.position, inline = True)
            embed.add_field(name = "Colour:", value = role.colour, inline = True)
            embed.add_field(name = "Hoisted:", value = role.hoist, inline = True)
            embed.add_field(name = "Mentionable:", value = role.mentionable, inline = True)
            embed.add_field(name = "Intergration:", value = role.managed, inline = True)   
            embed.add_field(name = f'Permissions', value = ", ".join(has_perm).replace("_"," ").title(), inline = False)
            await ctx.reply(embed = embed)

    

    @cog_ext.cog_subcommand(base = "channel", name = "info", description = "Show some information about the given channel.", options = [create_option(name = "channel", description = "Channel argument is required.", option_type = 7, required = True,)])
    async def _channelinfo(self, ctx: SlashContext, channel : Union[discord.TextChannel, discord.VoiceChannel, discord.StageChannel, discord.CategoryChannel]):
        with ctx.channel.typing():
            embed = discord.Embed(title = f"{channel.name}", description = f"{channel.mention} was created <t:{int(channel.created_at.timestamp())}:R>", colour = ctx.author.colour)
            embed.set_author(name = f"ID: {channel.id}")
            if channel.category == None:
                embed.add_field(name = "Category", value = "None", inline = True)
            else:
                embed.set_footer(text = f"Category ID: {channel.category.id}")
                embed.add_field(name = "Category", value = channel.category, inline = True)
            embed.add_field(name = "Position", value = channel.position, inline = True)
            if channel in ctx.guild.text_channels:
                embed.add_field(name = "Slowmode Delay", value = channel.slowmode_delay, inline = True)
                embed.add_field(name = "Topic", value = channel.topic, inline = False)
                embed.add_field(name = "Announcement:", value = channel.is_news(), inline = True)

            elif channel in ctx.guild.categories:
                embed.add_field(name = "Channels", value = len(channel.channels), inline = True)
                embed.add_field(name = "Text", value = len(channel.text_channels), inline = True)
                embed.add_field(name = "Voice", value = len(channel.voice_channels), inline = True)
                embed.add_field(name = "Stage", value = len(channel.stage_channels), inline = True)

            elif channel in ctx.guild.voice_channels or channel in ctx.guild.stage_channels:
                embed.add_field(name = "Bitrate", value = channel.bitrate, inline = True)
                embed.add_field(name = "Region", value = "Automatic" if channel.rtc_region == None else channel.rtc_region, inline = True)
                embed.add_field(name = "user Limit", value = channel.user_limit, inline = True)
                embed.add_field(name = "Voice states", value = channel.voice_states, inline = True)
                if channel in ctx.guild.stage_channels:
                    embed.add_field(name = "Topic", value = channel.topic, inline = False)
                    embed.add_field(name = "Requesting to speak", value = len(channel.requesting_to_speak), inline = True)
            embed.add_field(name = "Type:", value = channel.type, inline = True)
            embed.add_field(name = "Synced:", value = channel.permissions_synced, inline = True)
            await ctx.reply(embed = embed)
    
    @cog_ext.cog_subcommand(base = "channel", name = "topic", description = "Show a channels topic.", options = [create_option(name = "channel", description = "Channel argument is optional.", option_type = 7, required = False,)])
    async def _topic(self, ctx: SlashContext, channel : discord.TextChannel):
        channel = ctx.channel if channel is None else channel
        await ctx.reply(embed = discord.Embed(title = channel.name, description = channel.topic, colour = ctx.author.colour))

    @commands.command(description = "See the ID of any discord object.", usage = "[member][channel]")
    async def id(self, ctx: SlashContext, member : discord.Member = None, role : discord.Role = None, text : discord.TextChannel = None, voice : discord.VoiceChannel = None, stage : discord.StageChannel = None, category : discord.CategoryChannel = None):
        if member:
            await ctx.reply(f"{member.mention}: {member.id}")
        if role:
            await ctx.reply(f"{role.mention}: {role.id}")
        if text:
            await ctx.reply(f"{text.mention}: {text.id}")
        if voice:
            await ctx.reply(f"{voice.mention}: {voice.id}")
        if stage:
            await ctx.reply(f"{stage.mention}: {stage.id}")
        if category:
            await ctx.reply(f"{category.mention}: {category.id}")

    @cog_ext.cog_slash(name = "id", description = "Show a discord objects ID.", options = [
        create_option(
            name = "channel", 
            description = "gets the ID of a channel.", 
            option_type = 7, 
            required = False,
            ), 
        create_option(
            name = "member", 
            description = "gets the ID of a member", 
            option_type = 6,
            required = False
            ),
        create_option(
            name = "role", 
            description = "gets the ID of a role", 
            option_type = 8, 
            required = False,
            )
        ])
    async def _id(self, ctx: SlashContext, member : discord.Member = None, role : discord.Role = None, text : discord.TextChannel = None, voice : discord.VoiceChannel = None, stage : discord.StageChannel = None, category : discord.CategoryChannel = None):
        if member:
            await ctx.reply(f"{member.mention}: {member.id}")
        if role:
            await ctx.reply(f"{role.mention}: {role.id}")
        if text:
            await ctx.reply(f"{text.mention}: {text.id}")
        if voice:
            await ctx.reply(f"{voice.mention}: {voice.id}")
        if stage:
            await ctx.reply(f"{stage.mention}: {stage.id}")
        if category:
            await ctx.reply(f"{category.mention}: {category.id}")
    @commands.command(description = "Get a link to my support server.", usage = "support", aliases = ["server"])
    async def support(self, ctx):
        await ctx.reply(embed = discord.Embed(title = "Support Server", description = "https://discord.gg/wjWJwJB", colour = self.bot.primary_colour,))

    @checks.is_admin()
    @commands.command(description = "Get the link to ModMail's website.", usage = "website")
    async def website(self, ctx):
        await ctx.reply(embed = discord.Embed(title = "Website", description="https://modmail.xyz", colour=self.bot.primary_colour,))

    @commands.command(description = "Get the link to the bots GitHub repository.", usage="source", aliases=["github"])
    async def source(self, ctx):
        await ctx.reply(embed = discord.Embed(title = "GitHub Repository", description = "https://github.com/chamburr/modmail", colour = self.bot.primary_colour,))

    @cog_ext.cog_slash(name = "source", description = "Get the link to the bots GitHub repository.",)
    async def _source(self, ctx: SlashContext):
        await ctx.reply(embed = discord.Embed(title = "GitHub Repository", description = "https://github.com/chamburr/modmail", colour = self.bot.primary_colour,))


    @cog_ext.cog_subcommand(base = "user", name = "status", description = "Show a users avatar.", options = [create_option(name = "member", description = "If no member is given it will show your information.", option_type = 6, required = False,)])
    async def _status(self, ctx: SlashContext, member: discord.Member = None):
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            member_status = "No status" if member.activity is None else member.activity.name
            
            embed = discord.Embed(title = f"{member}", description = f"Status: **{member.status}**\n*{member_status}*", colour = member.colour)
            embed.set_author(name = f"{member.id}", icon_url = member.avatar_url)
            embed.set_thumbnail(url = member.avatar_url)
            await ctx.reply(embed = embed)

    @cog_ext.cog_slash(name = "emoji-info", description = "Show info about a emoji.", options = [create_option(name = "emoji", description = "emoji argument is required.", option_type = 3, required = True,)])
    async def _emoji(self, ctx: SlashContext, emoji: str):
        emoj_object = discord.Object(emoji)
        try:
            if isinstance(emoji, discord.PartialEmoji or discord.Emoji):
                embed = discord.Embed(title = f"{emoj_object.name}", description = f"Created <t:{int(emoj_object.created_at.timestamp())}:R>", colour = ctx.author.colour)
                embed.set_author(name = f"{emoj_object.id}", icon_url = emoj_object.url)
                embed.set_thumbnail(url = emoj_object.url)
                embed.add_field(name = "Raw Format", value = f"`<a:{emoj_object.name}:{emoj_object.id}>`" if emoji.animated == True else f"`<:{emoj_object.name}:{emoj_object.id}>`")
                await ctx.reply(embed = embed)
        except Exception:
            await ctx.reply(f"{Exception}")

    @commands.guild_only()
    @commands.command(description = "Get some information about a invite.", usage = "inviteinfo", aliases = ["invitestats", "ii"],)
    async def inviteinfo(self, ctx, invite: discord.Invite):
        invites = await ctx.guild.invites()
        for inv in invites:
            if inv.code == invite.code:
                embed = discord.Embed(title = f"Server invite: {invite.code}", description = f"Invite created <t:{int(inv.created_at.timestamp())}:R>", colour = ctx.author.colour, url = invite.url)
                embed.set_author(name = f"ID/Code: {invite.id}", icon_url = invite.guild.icon_url)
                embed.add_field(name = "Inviter", value = f"{invite.inviter.mention}" if invite.inviter else "Unknown")
                embed.add_field(name = "Uses", value = f"{inv.uses}/{'Infinite' if inv.max_uses == 0 else inv.max_uses}", inline = True)
                #embed.add_field(name = "Expires", value = f"<t:{int(invite.max_age.timestamp())}:R>", inline = True)
                embed.add_field(name = "Channel", value = f"{invite.channel.mention}", inline = True)
                embed.set_footer(text = f"{invite.inviter}", icon_url = invite.inviter.avatar_url)
                await ctx.reply(embed = embed)

    @commands.command(description = "Syncs the guilds template.", usage = "sync")
    async def sync(self, ctx):
        templates = await ctx.guild.templates()
        for template in templates:
            await template.sync()
            await ctx.reply(f"{template.name} synced")

def setup(bot):
    bot.add_cog(Info(bot))
