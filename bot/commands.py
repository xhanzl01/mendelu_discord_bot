import logging
from random import randint

import discord
from discord.ext import commands
from discord.utils import get
from verification import verification
from db.db import check_for_existing_uid, insert_new_student

bot = commands.Bot(command_prefix='$', help_command=None)
bot_token = "OTUxNTQwNTc3NDU4MDkwMDg1.Yio9OA.VlMspAKfMSBI2erNTtbAvhz5vfg"


@bot.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def give_role(ctx, user: discord.Member, role: discord.Role):
    if not (ctx.message.author.guild_permissions.administrator or "Moderator" in ctx.message.author.roles):
        return
    await user.add_roles(role)


# Overloading help command TODO FINISH
@bot.command(pass_context=True)
@commands.has_any_role("Verified", "Unverified")
async def help(ctx):
    embed = discord.Embed(
        colour=discord.Colour.orange()
    )
    embed.set_author(name="Help")
    embed.add_field(name="Test", value="testing shit", inline=False)

    if ctx.message.author.guild_permissions.administrator or "Moderator" in ctx.message.author.roles:
        embed.add_field(name="give_role",
                        value="This command accepts two arguments - name/id of discord user you want to give the role "
                              "to, and **exact** name of the role you want to give them.",
                        inline=False)

    embed.add_field(name="week", value="Returns number of the study week", inline=False)
    await ctx.message.author.send(embed=embed)


@bot.command()
@commands.has_role("Unverified")
async def verify(ctx, email, uid):
    # Check if message was sent to verify channel
    if ctx.channel.name != "verify":
        ctx.message.author.send("Use verify channel for this command please.")
        return
    # Check whether given uid is bind
    fullname = verification.is_valid_student(uid)
    if fullname == 0:
        await ctx.message.author.send("Wrong UID! It looks like this on your ISIC: 10012345")
        return
    # whether uid is not used already
    if check_for_existing_uid(uid):
        logging.CRITICAL("Someone tried to use UID that is already used: " + uid)
        await ctx.message.author.send("This UID is already used, please contact a moderator.")
        return
    # whether email is in valid form
    if not verification.is_valid_email(email):
        await ctx.message.author.send("Wrong e-mail! It must be in this form: xlogin@mendelu.cz")
        return

    # Sending verification email with token
    await ctx.message.author.send(f"Sending verification email to address `{email}`")
    token = randint(0, 2147483648)
    verification.send_mail(email, token)

    def check(message):
        return message.author == ctx.message.author and message.content == token

    # TODO TOKEN HANDLING
    msg = await bot.wait_for("message", check=check)
    ctx.message.author.send(msg)
    if 1:
        split_fullname = fullname.split(" ")
        if len(split_fullname) < 2:
            logging.WARNING("Too short fullname from UID: " + uid)
            insert_new_student(fullname, "", ctx.message.author.id, email.split("@")[0], uid, 0, "", "")
        if len(split_fullname) > 2:
            logging.WARNING("Too long fullname from UID: " + uid)
            insert_new_student(fullname[:-1], fullname[-1], ctx.message.author.id, email.split("@")[0], uid, 0, "", "")
        insert_new_student(fullname[0], fullname[1], ctx.message.author.id, email.split("@")[0], uid, 0, "", "")

        role = ctx.discord.utils.get(ctx.message.author.guild.roles, name="Verified")
        await ctx.message.author.add_roles(role)
        logging.info("New Verification for user " + ctx.message.author)


@verify.error
async def verify_error(ctx, error):
    if str(error).startswith("email"):
        await ctx.message.author.send(
            "Wrong **email** format. Please use !verify like this: `!verify xlogin@mendelu.cz UID`")
        return
    if str(error).startswith("uid"):
        await ctx.message.author.send(
            "Wrong **uid** format. Please use !verify like this: `!verify xlogin@mendelu.cz UID`")
        return
    await ctx.message.author.send("Unexpected error has occurred, please contact a moderator.")
    logging.error("Unexpected error with VERIFY command: " + error)


@bot.event
async def on_ready():
    logging.info(f"{bot} has logged in!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Me Robot'))


@bot.event
async def on_member_join(member):
    logging.info(f"{member} has logged to the server!")

    # giving role "Unverified"
    role = discord.utils.get(member.guild.roles, name="Unverified")
    await member.add_roles(role)

    # sending welcome message
    welcome_channel = bot.get_channel(951947206682898432)
    await welcome_channel.send(f"{member.mention} just joined the server! Can they verify though?")


@bot.event
async def on_member_update(before, after):
    promotion_channel = bot.get_channel(951949130912129104)
    if "Unverified" in before.roles and "Verified" in after.roles:
        await promotion_channel.send(f"{after.mention} just verified and can use the server now!")
    if "Bakalář" in after.roles:
        await promotion_channel.send(f"{after.mention} just promoted to Bc! Congratulations!")
    if "Helper" in after.roles:
        await promotion_channel.send(f"{after.mention} just promoted to Helper! Congratulations!")


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if reaction.message.channel.name != "rooms":
        if reaction.emoji.name == "Thanks":
            # todo karma
            return
        return
    messages = str.split(reaction.message.content, "\n")

    for msg in messages:
        # is this channel in the channel pool
        emoji = str.split(msg)[0]
        if str(emoji) == str(reaction.emoji):
            channel_name = str.split(msg)[1]
            channel = get(reaction.message.guild.channels, name=channel_name)
            if not channel:
                # if room doesn't exist, create it
                channel = await reaction.message.guild.create_text_channel(name=channel_name,
                                                                           category=reaction.message.channel.category)
                overwrite = channel.overwrites_for(reaction.message.guild.get_role(951625866968985640))

                # set all ppl not to see this channel
                overwrite.send_messages = False
                overwrite.read_messages = False
                # verified
                await channel.set_permissions(reaction.message.guild.get_role(951625866968985640), overwrite=overwrite)

            overwrite = channel.overwrites_for(reaction.message.guild.get_role(951625866968985640))
            # set only the user who reacted to see this channel
            overwrite.send_messages = True
            overwrite.read_messages = True
            await channel.set_permissions(user, overwrite=overwrite)


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    room_channel = bot.get_channel(payload.channel_id)  # room channel
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)  # message that is reacted to
    user = await bot.fetch_user(payload.user_id)  # user reacting to the message

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
            overwrite = channel.overwrites_for(message.guild.get_role(951625866968985640))
            # set only the user who reacted to see this channel
            overwrite.send_messages = False
            overwrite.read_messages = False
            await channel.set_permissions(user, overwrite=overwrite)
            return


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


def init_commands():
    bot.run(bot_token)
