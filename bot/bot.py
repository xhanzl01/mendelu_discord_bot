import logging

import discord
from discord.ext import commands

intents = discord.Intents.all()
discord.member = True

bot = commands.Bot(command_prefix='$', help_command=None, intents=intents)
bot_token = "OTUxNTQwNTc3NDU4MDkwMDg1.Yio9OA.VlMspAKfMSBI2erNTtbAvhz5vfg"


def init_bot():
    try:
        bot.run(bot_token)
    except Exception as ex:
        logging.error("Error while starting: " + ex)