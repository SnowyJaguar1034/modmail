async def parent(self, ctx):
    group_commands = []
    for command in ctx.command.commands:
        command_string = f"`{ctx.prefix + command.name}`"
        group_commands.append(command_string)
    await ctx.reply(embed = discord.Embed(title = f"Commands in `{ctx.command.name}`", description = " ".join(group_commands)))

@commands.group(name = "user", aliases = ["member"], invoke_without_command = True, case_insensitive = True,)
async def user_group(self, ctx):
    await self.parent(ctx)
    
@commands.guild_only()
@commands.has_permissions(manage_guild = True)
@user_group.command(name = "permissions", description = "Show a member's permission in a channel when specified.", usage = "[member] [channel]", aliases = ["perms"])
async def mpermissions(self, ctx, member: discord.Member = None, channel: Union[discord.TextChannel, discord.VoiceChannel, discord.StageChannel, discord.CategoryChannel] = None):
    channel = channel or ctx.channel
    member = member or ctx.author
    permissions = channel.permissions_for(member)
    embed = discord.Embed(title="Permission Information", colour = member.colour)
    embed.add_field(name="User", value=str(member), inline=False)
    embed.add_field(name = "Allowed", value = ", ".join([self.bot.tools.perm_format(name) for name, value in permissions if value]), inline = False)
    embed.add_field(name = "Denied", value=", ".join([self.bot.tools.perm_format(name) for name, value in permissions if not value]), inline = False)
    await ctx.reply(embed=embed)

@commands.group(name = "role", invoke_without_command = True, case_insensitive = True, aliases = ["rank"])
async def role_group(self, ctx):
    await self.parent(ctx)

@user_group.command(name = "permissions", description = "Show the members of the role specified.", usage = "[role]", aliases = ["perms"])
async def rpermissions(self, ctx, role: discord.Role):
    has_perm = [perm for perm in self.bot.config.role_perms if getattr(role.permissions, perm)]
    await ctx.reply(embed = discord.Embed(title = f"Permissions for {role}", description = f" ".join(has_perm)))


@user_group.command(name = "info", description = "Show some information about yourself or the member specified.", usage = "[member]", aliases = ["whois", "ui"])
async def zinfo(self, ctx, member: discord.Member = None):
    print(f"Author: {ctx.author}\nMember: {member}")
    member = ctx.author if member is None else member
    print(f"Author: {ctx.author}\nMember: {member}")        
    roles = [f"<@&{role.id}>" for role in member.roles]
    has_key = [perm for perm in self.bot.config.key_perms if getattr(member.guild_permissions, perm)]
    if len(has_key) == 0:
        has_key.append('No permissions')
    member_status = "No status" if member.activity is None else member.activity.name
    if len(roles) == 0:
        roles.append("No roles")

    embed = discord.Embed(title = f"{member.name}#{member.discriminator}", description = f"Status: **{member.status}**\n*{member_status}*", colour = member.colour)
    embed.set_author(name = f"{member.id}", icon_url = member.avatar_url)
    embed.set_thumbnail(url = member.avatar_url)
    embed.add_field(name = "Joined Server:", value = f"<t:{int(member.joined_at.timestamp())}:R>", inline = True)
    embed.add_field(name = "Avatar", value = f"[PNG]({member.avatar_url_as(static_format='png')})", inline = True)
    embed.add_field(name = "Joined Discord:", value = f"<t:{int(member.created_at.timestamp())}:R>", inline = True) 
    embed.add_field(name = f"Roles: {len(roles)}",value = f"{len(roles)} roles" if len(" ".join(roles)) > 1000 else " ".join(roles), inline = False)
    embed.add_field(name =f'Key permissions', value = ", ".join(has_key).replace("_"," ").title(), inline = False)
    await ctx.reply(embed = embed)

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