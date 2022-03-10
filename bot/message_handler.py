import discord

# Initiating discord client
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def handle_message(message):
