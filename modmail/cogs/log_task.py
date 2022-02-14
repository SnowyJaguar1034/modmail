import discord
from discord.ext import commands

class LogTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def moderation_logs(self, ctx):
        snowyjaguar = self.bot.get_user(self.bot.config.owner)
        checked_logs = []
        case_count = 0
        last_checked = 0
        bots = [776782769312628746, 719990867816874005] # Dyno: 617596472917229569
        moderation = await self.bot.fetch_channel(885569667861717042)
        clifford_log = await self.bot.fetch_channel(500768218257031168)
        # Field One: User who was moderated *
        # Field Two: Moderator who performed the moderation *
        # Field Three: Reason for moderation
        # Field Four: Duration of moderation

        async with moderation.typing():
            messages = await clifford_log.history(oldest_first = True, limit = None, after = last_checked).flatten() # 10000
            print(f"\nAll messages: {messages}")
            for message in messages[0:]: # Making bot search history chronologically
                print(f"\nBefore if: {message}")
                if message.webhook_id:
                    print(f"Webhook ID: {message.webhook_id}")
                if all([
                    message.id not in checked_logs, 
                    message.webhook_id == 719990867816874005, 
                    #message.author.id in bots, # Checks if the message author is my log bot
                    #len(message.embeds) > 0, # checks if the mesage contains embeds
                ]):
                    print(f"after if: {message}")
                    action = [word for word in self.bot.config.key_words if word in message.embeds[0].title]
                    if len(action) > 0:
                    #if action := [word for word in self.bot.config.key_words if word in message.embeds[0].title]:
                        print(f"\nWord: {action}")
                        embed = discord.Embed(title = f"Case {case_count} | {action[0]}", colour = self.bot.config.error_colour, timestamp = message.timestamp)
                        embed.set_author(name = f"{message.embeds[0].fields[0].value} | {message.embeds[0].fields[0].value.id}", icon_url = message.embeds[0].fields[0].value.avatar_url)
                        embed.set_footer(text = f"{message.embeds[0].fields[1].value} | {message.embeds[0].fields[1].value.id}", icon_url = message.embeds[0].fields[1].value.avatar_url)
                        embed.add_field(name = "Offender", value = message.embeds[0].fields[0].value, inline = True)
                        embed.add_field(name = "Moderator", value = message.embeds[0].fields[1].value, inline = True)
                        if message.embeds[0].fields[3]:
                            embed.add_field(name = "Duration", value = message.embeds[0].fields[3].value)
                        if message.embeds[0].fields[2]:
                            embed.add_field(name = "Reason", value = message.embeds[0].fields[2].value)
                        checked_logs.append(message.id)
                        print(f"\nEmbed: {embed}")
                        print(f"Case Count: {case_count}")

                        await moderation.send(embed = embed)
            await snowyjaguar.send(f"`{len(messages)}` were checked in {clifford_log.mention}, `{case_count}` logs were logged in {moderation.mention}")

def setup(bot):
    bot.add_cog(LogTask(bot))
    #print("Custom Commands are ready")