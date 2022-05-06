import logging

import discord
from discord.utils import get
from db.db import update_studies


async def add_permission_to_room(guild: discord.Guild, msg, rooms_channel: discord.TextChannel, member: discord.Member):
    channel_name = str.split(msg)[1]
    channel = get(guild.channels, name=channel_name)
    if not channel:  # does the channel exist?
        # if room doesn't exist, create it
        channel = await guild.create_text_channel(name=channel_name, category=rooms_channel.category)
        overwrite = channel.overwrites_for(guild.get_role(951625866968985640))

        # set all ppl not to see this channel
        overwrite.send_messages = False
        overwrite.read_messages = False
        # verified
        await channel.set_permissions(guild.get_role(951625866968985640), overwrite=overwrite)
    overwrite = channel.overwrites_for(guild.get_role(951625866968985640))
    # set only the user who reacted to see this channel
    overwrite.send_messages = True
    overwrite.read_messages = True
    await channel.set_permissions(member, overwrite=overwrite)


async def add_classification(guild: discord.Guild, msg, member: discord.Member):
    prvak = get(guild.roles, name="Prvák")
    druhak = get(guild.roles, name="Druhák")
    tretak = get(guild.roles, name="Třeťák")
    lajdak = get(guild.roles, name="Lajdák")

    ari = get(guild.roles, name="ARI")
    oi = get(guild.roles, name="OI")
    aii = get(guild.roles, name="AII")

    wanted_role_name = str.split(msg)[1]
    wanted_role = get(guild.roles, name=wanted_role_name)
    try:
        if wanted_role_name == "Prvák":
            await member.remove_roles(prvak, druhak, tretak, lajdak)
            update_studies("year_of_studies", 1, member.id)
        elif wanted_role_name == "Druhák":
            await member.remove_roles(prvak, druhak, tretak, lajdak)
            update_studies("year_of_studies", 2, member.id)
        elif wanted_role_name == "Třeťák":
            await member.remove_roles(prvak, druhak, tretak, lajdak)
            update_studies("year_of_studies", 3, member.id)
        elif wanted_role_name == "ARI" or wanted_role_name == "OI" or wanted_role_name == "AII":
            update_studies("program", wanted_role_name, member.id)
            await member.remove_roles(ari, oi, aii)
        await member.add_roles(wanted_role)  # give member the role
    except Exception as ex:
        logging.error(ex)
