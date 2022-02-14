import asyncio
import typing
import discord
from discord import Embed
from discord.ext import commands
from typing import Optional, Union

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.suggestions = 715617177209798677 # A_channel_ID

    @commands.command(description = "Lets users locate a specfic suggestion via it's message ID or link.", usage = "sug <[messsage link|ID] | [phrase]>", aliases = ["find", "find-sug", "search", "search-sug"])
    async def test_sug(self, ctx, search: Union[discord.Message, str]):
        suggestions = self.bot.get_channel(id = self.suggestions)
        if isinstance(search, discord.Message):
            await ctx.reply(embed = search.embeds[0].copy(),) # components = """Needs a button linking to the message"""
        else:
            with ctx.typing():
                matches = 0
                output = " "
                messages = await suggestions.history(limit = None, before = None, after = None, around = None, oldest_first = None).flatten()
                for message in messages:
                    if len(message.embeds) > 0:
                        if search in message.embeds[0].author.name:
                            matches += 1
                            output = (output + f"[{message.embeds[0].author.name}]({message.jump_url})")

                embed = Embed(title = f"I found `{matches}` suggestions matching `{search}`.", description = output)
                await ctx.reply(embed = embed)

    @commands.command(description = "Dehost user nicknames.", usage = "deshoist")
    async def dehoist(self, ctx, member : Optional[discord.Member]):
        with ctx.channel.typing():
            count = 0
            hoistlist = ["!","@","#","$","%","^","&","*","(",")",",",".","~","`"]
            for member in ctx.guild.members:
                for hoist in hoistlist:
                    if member.display_name.startswith(str(hoist)):
                        count += 1
                        newname = member.display_name.translate(str.maketrans('','','!@#$%^&*()~.,><:"/?\|'))
                        await member.edit(nick = newname)
            await ctx.channel.send(f"changed the nickname of {count} members")

def setup(bot):
    bot.add_cog(Suggestions(bot))