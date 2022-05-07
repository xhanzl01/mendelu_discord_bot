import logging

import discord
from discord.ext import commands

from features.commands import init_commands
from features.events import init_events

intents = discord.Intents.all()
discord.member = True

bot_token = "OTUxNTQwNTc3NDU4MDkwMDg1.Yio9OA.VlMspAKfMSBI2erNTtbAvhz5vfg"
bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)


def init_bot():
    try:
        bot.run(bot_token)

        init_events(bot)
        init_commands(bot)
    except Exception as ex:
        logging.error("Error while starting: " + str(ex))
