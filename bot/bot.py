import discord



def has_role(message, roleName):
    role = discord.utils.get(message.author.guild.roles, name=roleName)
    if role in message.author.roles:
        return True
    return False

async def verification(message):
    pass

def test():
    dict = {
        "verify": verification,
    }