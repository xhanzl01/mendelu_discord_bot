import logging

import discord
from discord.ext import commands

from features.commands import init_commands
from features.events import init_events

intents = discord.Intents.all()
discord.member = True

bot_token = "insert your token here"
bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)


def init_bot():
    try:
        init_events(bot)
        init_commands(bot)
        bot.run(bot_token)
    except Exception as ex:
        logging.error("Error while starting: " + str(ex))
