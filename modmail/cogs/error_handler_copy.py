import logging, traceback, discord, sys
from discord.ext import commands
log = logging.getLogger(__name__)

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.on_command_error = self._on_command_error

    async def _on_command_error(self, ctx, error, bypass=False):
        snowyjaguar = self.bot.get_user(self.bot.config.owner)
        if (
            hasattr(ctx.command, "on_error")
            or (ctx.command and hasattr(ctx.cog, f"_{ctx.command.cog_name}__error"))
            and not bypass
        ):
            return
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                embed=discord.Embed(title="Command Unavailable",description="This command cannot be used in direct message.",colour=self.bot.error_colour,))
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(
                embed=discord.Embed(title="Command Unavailable", description="This command can only be used in direct message.", colour=self.bot.error_colour,))
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Invalid Arguments", description=f"Please check the usage below or DM {snowyjaguar.mention} if you don't know what went wrong.", colour=self.bot.error_colour,)
            usage = "\n".join([ctx.prefix + x.strip() for x in ctx.command.usage.split("\n")])
            embed.add_field(name="Usage", value=f"```{usage}```")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            await ctx.send(embed=discord.Embed(title="Permission Denied", description="You do not have permission to use this command.", colour=self.bot.error_colour,))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(title="Permission Denied",description="You do not have permission to use this command. Permissions needed: {', '.join([self.bot.tools.perm_format(p) for p in error.missing_perms])}", colour=self.bot.error_colour,))
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=discord.Embed(title="Bot Missing Permissions", description="Bot is missing permissions to perform that action. Permissions needed: {', '.join([self.bot.tools.perm_format(p) for p in error.missing_perms])}", colour=self.bot.error_colour,))
        elif isinstance(error, discord.HTTPException):
            await ctx.send(embed=discord.Embed(title="Unknown HTTP Exception",description=f"Please report this in the support server.\n```{error.text}````", colour=self.bot.error_colour,))
        elif isinstance(error, commands.CommandInvokeError):
            guild = ctx.channel.id if ctx.guild.id == None else ctx.guild.id
            log.error(f"{error.original.__class__.__name__}: {error.original} (In {ctx.command.name})\n{guild}\nTraceback:\n{''.join(traceback.format_tb(error.original.__traceback__))}"
            )
            #try:
            await ctx.send(embed=discord.Embed(title="Unknown Error",description="Please report this in the support server.\n```{error.original.__class__.__name__}: {error.original}```", colour=self.bot.error_colour,))
            #except Exception:
                #pass
        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            log.error('Ignoring exception in command {ctx.command}:', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
