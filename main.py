#Modules
import discord
import logging
import os
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')
AI_token = ""
modelType = ""

#Exporting .txt file into list
with open("supportedmodels.txt", 'r') as file:
    lines = file.readlines()
modelLists = [line.strip() for line in lines] #model lists


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

async def askAI(ctx, prompt: str, model: str, api: str):
    try:
        genai.configure(api_key=api)
        model_instance = genai.GenerativeModel(model_name=model)
        response = model_instance.generate_content(prompt)
        await ctx.send((response.text or "No response.")[:1000])
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")


@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user} (ID: {bot.user.id})")

@bot.command()
async def API(ctx, *, message):
    global AI_token
    if not modelType:
        await ctx.send("Please set the model type first using `/model <model_name>`.")
        return
    else:
        AI_token = message
        await ctx.send(f"API token has been set!")

@bot.command()
async def model(ctx, *, message):
    global modelType
    if message == "status":
        if not modelType:
            await ctx.send("Model type is not set. Please set it using `/model <model_name>`.")
        else:
            await ctx.send(f"Current model type is: {modelType}")
        return
    if message not in modelLists:
        await ctx.send(f"Invalid model type. Here is a list of valid models: {modelLists}") #edit this with github .txt link
        return
    else:
        modelType = message
        await ctx.send(f"Model type has been set to {modelType}!")
        return

@bot.command()
async def ask(ctx,*, prompt:str):
    if not AI_token and modelType:
        await ctx.send("Please set the API token first using `/API <token>`")
        return
    if not modelType and AI_token:
        await ctx.send("Please set the model type first using `/model <model_name>`.")
        return
    if not AI_token and not modelType:
        await ctx.send("Please set the API token and model type first using `/API <token>` and `/model <model_name>`.")
        return
    if modelType == "gemini-1.5-flash":
        await askAI(ctx, prompt, modelType, AI_token)

    

bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
