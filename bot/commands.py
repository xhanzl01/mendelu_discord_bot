import logging
import discord
from discord.ext import commands
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
    if ctx.message.channel != 951964914178736148:
        return
    # Check whether given uid is bind
    fullname = verification.is_valid_student(uid)
    if len(fullname) == 0:
        await ctx.send("Wrong UID! It looks like this on your ISIC: 10012345")
        return
    # whether uid is not used already
    if check_for_existing_uid(uid):
        logging.warning("Someone tried to use UID that is already used: " + uid)
        await ctx.send("This UID is already used, please contact a moderator.")
        return
    # whether email is in valid form
    if not verification.is_valid_email(email):
        await ctx.send("Wrong e-mail! It must be in this form: xlogin@mendelu.cz")
        return

    # Sending verification email with token
    await ctx.send(f"Sending verification email to address `{email}`")
    verification.send_mail(email)

    # TODO TOKEN HANDLING
    if await verification.check_token(1):
        split_fullname = fullname.split(" ")
        if len(split_fullname) < 2:
            logging.warning("Too short fullname from UID: " + uid)
            insert_new_student(fullname, "", ctx.message.author.id, email.split("@")[0], uid, 0, "", "")
        if len(split_fullname) > 2:
            logging.warning("Too long fullname from UID: " + uid)
            insert_new_student(fullname[:-1], fullname[-1], ctx.message.author.id, email.split("@")[0], uid, 0, "", "")
        insert_new_student(fullname[0], fullname[1], ctx.message.author.id, email.split("@")[0], uid, 0, "", "")

        role = ctx.discord.utils.get(ctx.message.author.guild.roles, name="Verified")
        await ctx.message.author.add_roles(role)
        logging.info("New Verification for user " + ctx.message.author)


@verify.error
async def verify_error(ctx, error):
    if str(error).startswith("email"):
        await ctx.send("Wrong **email** format. Please use !verify like this: `!verify xlogin@mendelu.cz UID`")
        return
    if str(error).startswith("uid"):
        await ctx.send("Wrong **uid** format. Please use !verify like this: `!verify xlogin@mendelu.cz UID`")
        return
    await ctx.send("Unexpected error has occurred, please contact a moderator.")
    logging.warning("Unexpected error with VERIFY command: " + error)


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
    verified_channel = bot.get_channel(951949130912129104)
    if "Unverified" in before.roles and "Verified" in after.roles:
        await verified_channel.send(f"{after.mention} just verified and can use the server now!")
    if "Bakalář" in after.roles:
        await verified_channel.send(f"{after.mention} just promoted to bc! Congratulations!")


@bot.event
async def on_raw_reaction_add(payload):
    pass


def init_commands():
    bot.run(bot_token)
