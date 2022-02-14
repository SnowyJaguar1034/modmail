import discord
from discord.ext import commands

class Custom_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def moderation_logs(self, ctx):
        snowyjaguar = self.bot.get_user(self.bot.config.owner)
        key_words = ["WARN", "MUTE", "UNMUTE", "KICK", "BAN", "UNBAN"] # Add in Captilised versions of each word to account for the Dyno logs
        checked_logs = []
        case_count = 0
        last_checked = 0
        #dict = {}
        moderation = self.bot.get_channel(id = 885569667861717042)
        clifford_log = self.bot.get_channel(id = 500768218257031168)
        # Field One: User who was moderated *
        # Field Two: Moderator who performed the moderation *
        # Field Three: Reason for moderation
        # Field Four: Duration of moderation

        with moderation.channel.typing():
            messages = await clifford_log.channel.history(oldest_first = True, limit = None, after = last_checked).flatten() # 10000
            for message in messages[0:]: # Making bot search history chronologically
                if message.id not in checked_logs:
                    if message.author.id == 776782769312628746:
                        if len(message.embeds) > 0:
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
            await snowyjaguar.send(f"`{len(messages)}` were checked in {clifford_log.mention}, `{case_count}` logs were logged in {moderation.mention}")

def setup(bot):
    bot.add_cog(Custom_Commands(bot))
    #print("Custom Commands are ready")