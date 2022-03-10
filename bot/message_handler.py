import discord
import bot

# Initiating discord client
intents = discord.Intents.default()
client = discord.Client(intents=intents)

config = {
    "verify": bot.verify,
    "help": bot.get_help,
    "meme": bot.get_meme,
    "week": bot.get_week,
    "uid": bot.get_uid,
}


@client.event
async def handle_message(message):
    pass
