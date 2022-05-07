import logging
import os
from random import randint
import discord
from discord.ext import commands

from verification import verification
from db.db import check_for_existing_uid, insert_new_student, return_all_students_in_db, get_token


def init_commands(bot):
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
        await ctx.message.delete()
        # Check if message was sent to verify channel
        if ctx.channel.name != "verify":
            ctx.author.send("Use verify channel for this command please.")
            return
        # Check whether given uid is bind
        fullname = verification.is_valid_student(uid)
        if fullname == 0 or fullname is None:
            await ctx.author.send("Wrong UID! It looks like this on your ISIC: 10012345")
            return
        # whether uid is not used already
        if check_for_existing_uid(uid):
            logging.critical("Someone tried to use UID that is already used: " + uid)
            await ctx.author.send("This UID is already used, please contact a moderator.")
            return
        # whether email is in valid form
        if not verification.is_valid_email(email):
            await ctx.author.send("Wrong e-mail! It must be in this form: xlogin@mendelu.cz")
            return

        # Sending verification email with token
        await ctx.author.send(f"Sending verification email to address `{email}`")
        random_token = randint(1, 2147483648)

        verification.send_mail(email, random_token)

        split_fullname = fullname.split(" ")
        if len(split_fullname) < 2:
            logging.warning("Too short fullname from UID: " + uid)
            insert_new_student(fullname, "", ctx.message.author.id, email.split("@")[0], uid, 0, "", random_token)
        elif len(split_fullname) > 2:
            logging.warning("Too long fullname from UID: " + uid)
            insert_new_student(split_fullname[:-1], split_fullname[-1], ctx.message.author.id, email.split("@")[0],
                               uid, 0, "", random_token)
        else:
            insert_new_student(split_fullname[0], split_fullname[1], ctx.message.author.id, email.split("@")[0],
                               uid, 0, "", random_token)

    @bot.command()
    @commands.has_role("Unverified")
    async def token(ctx, message_token):
        # get token
        try:
            int_token = int(message_token)
        except ValueError:
            logging.error(f"ValueError while verifying %s, token: %s", str(ctx.author.name), str(message_token))
            await ctx.message.author.send(
                "The token you have send is not correct. The token must be a number. If you think this is "
                "an error, please contact `F0uss#3807`.\n"
                "If you do not have a token, please first use !verify command to get one.")
        else:
            student = get_token(ctx.message.author.id)[0]
            if len(student) == 0:
                await ctx.message.author.send(
                    "It seems like you did not verify. Please head over to the #verify channel and "
                    "verify there.")
            # check if token is correct
            elif student[-2] == int_token:
                # find role in the roles pool
                verified_role = discord.utils.get(ctx.message.author.guild.roles, name="Verified")
                unverified_role = discord.utils.get(ctx.message.author.guild.roles, name="Unverified")

                # give user Verified role and remove Unverified role
                await ctx.message.author.add_roles(verified_role)
                await ctx.message.author.remove_roles(unverified_role)

                # send message user has promoted
                logging.info("New Verification for user " + str(ctx.author.name))
                try:
                    promotion_channel = bot.get_channel(951949130912129104)

                    await promotion_channel.send("New student has verified " + str(ctx.author.mention))
                except Exception as ex:
                    print(ex)
            else:
                await ctx.message.author.send(
                    "Wrong token, the token was sent to your school email address. Check spam "
                    "folder if you dont see it. If you think you entered a correct token, "
                    "please contact `F0uss#3807`")

    @verify.error
    async def verify_error(ctx, error):
        await ctx.message.delete()
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

    # deletes permissions in all rooms for all members and roles. Deletes all members roles but "Unverified" and "Mod"
    @bot.command()
    @commands.has_role("Mod")
    async def delete_permissions_for_all_rooms(ctx):  # deletes permissions for all roles and members in all rooms.
        roles_to_remove = []
        for role in ctx.guild.roles:
            if role.name.startswith("Mod") or role.name.startswith("SubMod") or role.name.startswith(
                    "Verified") or role.name.startswith("Unverified"):
                roles_to_remove.append(role)

        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.read_messages = False
        for channel in ctx.guild.channels:
            s = f"Deleting permissions in channel #{channel} "
            for member in ctx.guild.members:
                await channel.set_permissions(member, overwrite=overwrite)  # delete permissions in room for member
                logging.info(s + f"for member {member}")
            for role in ctx.guild.roles:
                await channel.set_permissions(role, overwrite=overwrite)  # delete permissions in room for role
                logging.info(s + f"for role {role}")

    @bot.command()
    @commands.has_role("Mod")
    async def remove_roles_from_all_users(ctx):  # removes all roles in all members

        for role in ctx.guild.roles:
            if not (role.name.startswith("Mod") or role.name.startswith("SubMod") or role.name.startswith("Verified")
                    or role.name.startswith("Unverified") or role.name.startswith("@everyone")
                    or role.name.startswith("PEFNet 2.0") or role.name.startswith("PEFNet 2.0")
                    or role.name.startswith("MendeluBot") or role.name.lower().startswith("bot")):
                for member in ctx.guild.members:
                    logging.info(f"Removing role {role} from member {member}")
                    await member.remove_roles(role)  # remove role from member

    @bot.command()
    async def ping(ctx):
        await ctx.send("pong")
