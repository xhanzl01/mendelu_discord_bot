import logging
from verification import verification
from db.db import check_for_existing_uid, insert_new_student
import discord

bot_token = "OTUxNTQwNTc3NDU4MDkwMDg1.Yio9OA.VlMspAKfMSBI2erNTtbAvhz5vfg"
# Initiating discord client
client = discord.Client()
guild = None


def has_role(message, roleName):
    """role = discord.utils.get(message.author.guild.roles, name=roleName)
    if role in message.author.roles:
        return True
    return False"""


@client.event
async def verify(message):
    split_message = message.content.split(" ")
    mail = split_message[1]
    uid = split_message[2]

    if len(split_message) != 3:
        await message.channel.send("Please use !verify in correct format like this: !verify xlogin@mendelu.cz UID")
        logging.warning("Someone tried to use UID that is already used: " + message.content)
        return
    fullname = verification.is_valid_student(uid)

    # Check whether given uid is bind
    if len(fullname) == 0:
        await message.channel.send("Wrong UID! It looks like this on your ISIC: 10012345")
        return
    # whether uid is not used already
    if check_for_existing_uid(uid):
        await message.channel.send("This UID is already used, please contact a moderator.")
        return
    # whether email is in valid form
    if not verification.is_valid_email(mail):
        await message.channel.send("Wrong e-mail! It must be in this form: xlogin@mendelu.cz")
        return

    # Sending verification email with token
    verification.send_mail(split_message[1])

    # TODO TOKEN HANDLING
    if await verification.check_token(1):
        split_fullname = fullname.split(" ")
        if len(split_fullname) < 2:
            logging.warning("Too short fullname: " + message.content)
            insert_new_student(fullname, "", message.author.id, mail.split("@")[0], uid, 0, "", "")
        if len(split_fullname) > 2:
            logging.warning("Too long fullname: " + message.content)
            insert_new_student(fullname[:-1], fullname[-1], message.author.id, mail.split("@")[0], uid, 0, "", "")
        insert_new_student(fullname[0], fullname[1], message.author.id, mail.split("@")[0], uid, 0, "", "")

        role = discord.utils.get(message.author.guild.roles, name="Verified")
        await message.author.add_roles(role)
        logging.debug("New Verification for user " + message.author)


@client.event
async def get_help(message):
    await message.channel.send("help")


@client.event
async def get_terms(message):
    await message.channel.send("terms")


@client.event
async def get_meme(message):
    await message.channel.send("meme")


@client.event
async def get_week(message):
    await message.channel.send("week")


@client.event
async def get_uid(message):
    await message.channel.send("uid")


@client.event
async def handle_message(message):
    pass


config = {
    "!verify": verify,
    "!help": get_help,
    "!meme": get_meme,
    "!week": get_week,
    "!uid": get_uid,
}


def getList(dict):
    return dict.keys()


def start_bot():
    client.run(bot_token)


@client.event
async def on_ready():
    logging.debug(f"{client} has logged in!")


@client.event
async def on_member_join(member):
    logging.debug(f"{member} has logged to the server!")
    role = discord.utils.get(member.guild.roles, name="Unverified")
    await member.add_roles(role)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # await config[message.content](message)
    msg = message.content.split(" ")
    if msg[0] in config:
        await config[msg[0]](message)
