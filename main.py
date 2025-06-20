#Modules
import discord
import logging
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user} (ID: {bot.user.id})")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
