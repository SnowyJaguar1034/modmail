
    @checks.is_mod()
    @commands.guild_only()
    @commands.command(description = "Create ticket for a member.", usage = "create <member> <message>")
    async def ticket(self, ctx, member: discord.Member, *, message: str):
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