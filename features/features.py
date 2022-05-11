import logging

import discord
from discord.utils import get
from db.db import update_studies


async def add_permission_to_room(guild: discord.Guild, msg, rooms_channel: discord.TextChannel, member: discord.Member):
    channel_name = str.split(msg)[1]
    channel = get(guild.channels, name=channel_name)
    verified_role = get(guild.roles, name="Verified")
    unverified_role = get(guild.roles, name="Unverified")

    if not channel:  # does the channel exist?
        # set all ppl not to see this channel
        overwrites = {
            verified_role: discord.PermissionOverwrite(read_messages=False),
            unverified_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True),
        }
        # verified
        channel = await guild.create_text_channel(name=channel_name, category=rooms_channel.category, overwrites=overwrites)
    # set only the user who reacted to see this channel
    await channel.set_permissions(member, read_messages=True)


async def add_classification(guild: discord.Guild, msg, member: discord.Member):
    prvak = get(guild.roles, name="Prvák")
    druhak = get(guild.roles, name="Druhák")
    tretak = get(guild.roles, name="Třeťák")
    lajdak = get(guild.roles, name="Lajdák")

    ari = get(guild.roles, name="ARI")
    oi = get(guild.roles, name="OI")
    aii = get(guild.roles, name="AII")
    bcoi = get(guild.roles, name="BcOI")
    ei = get(guild.roles, name="EI")

    wanted_role_name = str.split(msg)[1]
    wanted_role = get(guild.roles, name=wanted_role_name)
    if wanted_role_name == "Prvák":
        await member.remove_roles(prvak, druhak, tretak, lajdak)
        update_studies("year_of_studies", 1, member.id)
    elif wanted_role_name == "Druhák":
        await member.remove_roles(prvak, druhak, tretak, lajdak)
        update_studies("year_of_studies", 2, member.id)
    elif wanted_role_name == "Třeťák":
        await member.remove_roles(prvak, druhak, tretak, lajdak)
        update_studies("year_of_studies", 3, member.id)
    elif wanted_role.id == "ARI" or wanted_role_name == "OI" or wanted_role_name == "AII" or wanted_role_name == "EI" or wanted_role_name == "BcOI" or wanted_role_name == "EI":
        await member.remove_roles(ari)
        await member.remove_roles(oi)
        await member.remove_roles(aii)
        await member.remove_roles(ei)
        await member.remove_roles(bcoi)
        update_studies("program", wanted_role_name, member.id)

    await member.add_roles(wanted_role)  # give member the role
