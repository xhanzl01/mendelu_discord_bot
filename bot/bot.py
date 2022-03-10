import discord


def has_role(message, roleName):
    role = discord.utils.get(message.author.guild.roles, name=roleName)
    if role in message.author.roles:
        return True
    return False


async def verify(message):
    pass


async def get_help(message):
    pass


async def get_terms(message):
    pass


async def get_meme(message):
    pass


async def get_week(message):
    pass


async def get_uid(message):
    pass


