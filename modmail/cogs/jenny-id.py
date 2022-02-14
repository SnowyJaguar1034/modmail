@commands.command(description = "Show the ID of yourself or the member specified.", usage = "id [member]", aliases = ["user-id", "ID", "Id", "iD", "ui"])
async def id(self, ctx, *, member: discord.Member = None):
    await ctx.reply({member.id})