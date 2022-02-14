def setup(bot):
    bot.load_extension('jishaku')


''' @client.command()
async def eightball(ctx, message: str):
    # message is required to be inputted, if no message is given then the command fails with a invalid arg error (I think)
    responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
        "Don’t count on it.", "It is certain.", "It is decidedly so.", "Most likely.", "My reply is no.", "My sources say no.",
        "Outlook not so good.", "Outlook good.", "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.",
        "Yes.", "Yes – definitely.", "You may rely on it."]
    await ctx.send(f":8ball: {random.choice(responses)}") '''

if len(member._roles) == 0:
    value ="*None*"
else: 
    if len(" ".join([f"<@&{role}>" for role in member._roles])) <= 1024:
        value = " ".join([f"<@&{role}>" for role in member._roles])
    else:
        value = f"*{len(member._roles)} roles*",

value = "*None* "if len(member._roles) == 0 else " ".join([f"<@&{role}>" for role in member._roles]) if len(" ".join([f"<@&{x}>" for x in member._roles])) <= 1024 else f"*{len(member._roles)} roles*",


embed=discord.Embed()
embed.add_field(name = "Roles", value = "*None* " if len(member._roles) == 0 else ", ".join([f"<@&{role}>" for role in member._roles]) if len(" ".join([f"<@&{role}>" for role in member._roles])) <= 1024 else f"*{len(member._roles)} roles*",)