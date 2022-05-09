import logging
import discord
from discord.utils import get

from features.features import add_permission_to_room, add_classification


def init_events(bot):
    @bot.event
    async def on_ready():
        logging.info(f"{bot} has logged in!")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Me Robot'))

    @bot.event
    async def on_member_join(member: discord.Member):
        logging.info(f"{member} has logged to the server!")

        # giving role "Unverified"
        role = discord.utils.get(member.guild.roles, name="Unverified")
        await member.add_roles(role)

        welcome_channel = get(member.guild.channels, name="welcome")
        await welcome_channel.send(f"{member.mention} just joined the server! Can they verify though?")

        # send verification guide
        en_verify_embed = discord.Embed(title="",
                                     description="**Use both commands in the #verify channel on the server. DO NOT send "
                                                 "commands to the bot directly!\n\n** "
                                                 "To get started type `!verify xlogin@mendelu.cz userid` - where "
                                                 "xname@mendelu.cz is your university email and userid your ID Number on "
                                                 "your ISIC.\n\nThe bot will send you an email with a verification token "
                                                 "\n\n"
                                                 "After you receive the token use command !token *your token*.\n\n"
                                                 "If you did everything correctly, the bot will grant you permission to "
                                                 "the server. Now head to the #zařazení channel and use reactions to get"
                                                 "roles of your year of studies and study program."
                                                 ,
                                     colour=discord.Color.green())
        en_verify_embed.set_author(name="Verification",
                                icon_url="https://cdn4.iconfinder.com/data/icons/basic-ui-colour/512/ui-41-512.png")
        en_verify_embed.set_footer(
            text="**If you cannot verify, send message to Fouss#3807**.")

        cz_verify_embed = discord.Embed(title="",
                                     description="**Použij oba příkazy v kanále #verify. NEPOSÍLEJ příkazy botovi do zpráv!\n\n** "
                                                 "Začni tak, že napíšeš `!verify xlogin@mendelu.cz UID` kde xlogin@mendelu.cz je"
                                                 "tvůj univerzitní email a UID je ID na tvém ISICu (to kratší, né ISIC"
                                                 "card number začínající S 420..., toto číslo můžeš najít i na svém profilu v ISU)."
                                                 "\n\nBot ti pak pošle na tvůj univerzitní email token. Pokud ho nevidíš, koukni do spamu."
                                                 "\n\n"
                                                 "Jakmile dostaneš token napiš `!token *tvůj token*`.\n\n"
                                                 "Pokud jsi udělal vše správně, měl bys dostat roli *Verified*, zamiř"
                                                 "pak do kanálu #zařazení a vyklikej si pomocí reakcí ročník a obor.\n",
                                     colour=discord.Color.green())
        cz_verify_embed.set_footer(
            text="**Pokud se ti nedaří se verifikovat, prosím napiš zprávu Fouss#3807**")
        await member.send(embed=en_verify_embed)
        await member.send(embed=cz_verify_embed)

    @bot.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        # is user trying to get permissions to rooms?
        message: discord.Message = await bot.get_channel(payload.channel_id).fetch_message(
            payload.message_id)  # message that is reacted to
        channel: discord.TextChannel = bot.get_channel(payload.channel_id)  # channel that the reaction was added in
        reaction = get(message.reactions, emoji=payload.emoji.name)
        guild: discord.guild = bot.get_guild(payload.guild_id)
        if channel.name == "zařazení":
            messages = str.split(message.content, "\n")

            for msg in messages:
                # is this channel in the channel pool
                emoji = str.split(msg)[0]
                if str(emoji) == str(payload.emoji):
                    await add_classification(guild, msg, payload.member)
                    await reaction.remove(payload.member)
                    return
        elif channel.name == "rooms":
            messages = str.split(message.content, "\n")

            for msg in messages:
                # is this channel in the channel pool
                emoji = str.split(msg)[0]
                if str(emoji) == str(payload.emoji):
                    await add_permission_to_room(guild, msg, channel, payload.member)
                    return
        elif str(payload.emoji.name) == "Thanks":
            # todo karma
            pass
        else:
            return

    @bot.event
    async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
        room_channel = bot.get_channel(payload.channel_id)  # room channel
        message = await bot.get_channel(payload.channel_id).fetch_message(
            payload.message_id)  # message that is reacted to
        user = await bot.fetch_user(payload.user_id)  # user reacting to the message
        verified_role = get(bot.get_guild(payload.guild_id).roles, name="Verified")

        if room_channel.name != "rooms":
            if payload.emoji.name == "Thanks":
                # todo karma
                return
            return
        for msg in str.split(message.content, "\n"):
            emoji = str.split(msg)[0]
            channel_name = str.split(msg)[1]
            if str(emoji) == str(payload.emoji):
                channel = get(bot.get_guild(payload.guild_id).channels, name=channel_name)
                overwrite = channel.overwrites_for(verified_role)
                # set only the user who reacted to see this channel
                overwrite.send_messages = False
                overwrite.read_messages = False
                await channel.set_permissions(user, overwrite=overwrite)
                return

    @bot.event
    async def on_member_update(before, after):
        promotion_channel = get(before.guild.channels, id=972436866940936212)
        if "Unverified" in before.roles and "Verified" in after.roles:
            await promotion_channel.send(f"{after.mention} just verified and can use the server now!")
        if "BcOI" in after.roles:
            await promotion_channel.send(f"{after.mention} just promoted to Bc! Congratulations!")
        if "Helper" in after.roles:
            await promotion_channel.send(f"{after.mention} just promoted to Helper! Congratulations!")
