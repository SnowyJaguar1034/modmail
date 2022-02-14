import discord
from discord.ext import commands

class Custom_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    

def setup(bot):
    bot.add_cog(Custom_Commands(bot))
    #print("Custom Commands are ready")