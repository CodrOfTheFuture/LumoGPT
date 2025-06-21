#Modules
import discord
import logging
import os
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai
import openai
from openai import OpenAI


load_dotenv()

# variables
discord_token = os.getenv('DISCORD_TOKEN')
usersessions = {}

modelLists = {
    "gemini-1.5-flash" : "gemini", 
    "gemini-1.5-pro" : "gemini",
    "gemini-pro": "gemini",
    "llama3-8b-8192": "groq"
}

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

# Functions to ask different models
async def askGemini(ctx, prompt: str, model: str, api: str):
    try:
        genai.configure(api_key=api)
        model_instance = genai.GenerativeModel(model_name=model)
        response = model_instance.generate_content(prompt)
        await ctx.send((response.text or "No response.")[:1000])
    except Exception:
        await ctx.send(f"Error, it looks like the API token is invalid or you do not have enough credits to use this model!")


async def askGroq(ctx, prompt: str, model: str, api: str):
    try:
        client = OpenAI(
            api_key=api,
            base_url="https://api.groq.com/openai/v1"
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        await ctx.send((response.choices[0].message.content or "No response.")[:1000])
    except Exception as e:
        print(f"Groq API Error: {e}")
        await ctx.send(f"Error, it looks like the API token is invalid or you do not have enough credits to use this model!")

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user} (ID: {bot.user.id})")

#Discord commands
@bot.command()
async def API(ctx, *, message):
    user_id = ctx.author.id
    session = usersessions.setdefault(user_id, {})
    
    if "model" not in session:
        await ctx.send("Please set the model type first using `/model <model_name>`.")
        return
    
    session["api"] = message
    await ctx.send("API token has been set!")

@bot.command()
async def model(ctx, *, message):
    user_id = ctx.author.id
    session = usersessions.setdefault(user_id, {})

    if message == "status":
        model = session.get("model")
        if not model:
            await ctx.send("Model type is not set. Please set it using `/model <model_name>`.")
        else:
            await ctx.send(f"Current model type is: {model}")
        return

    if message not in modelLists:
        model_names = ', '.join(modelLists.keys())
        await ctx.send(f"Invalid model type. Valid models: {model_names}")
        return

    session["model"] = message
    await ctx.send(f"Model type has been set to {message}!")


@bot.command()
async def ask(ctx, *, prompt: str):
    user_id = ctx.author.id
    session = usersessions.get(user_id, {})

    model = session.get("model")
    api = session.get("api")

    if not api and model:
        await ctx.send("Please set the API token first using `/API <token>`.")
        return
    if not model and api:
        await ctx.send("Please set the model type first using `/model <model_name>`.")
        return
    if not model and not api:
        await ctx.send("Please set the API token and model type first using `/API <token>` and `/model <model_name>`.")
        return

    provider = modelLists.get(model)
    if provider == "gemini":
        await askGemini(ctx, prompt, model, api)
    elif provider == "groq":
        await askGroq(ctx, prompt, model, api)
    else:
        await ctx.send("Invalid or unsupported model selected.")

@bot.command()
async def reset(ctx):
    user_id = ctx.author.id
    usersessions.pop(user_id, None)
    await ctx.send("Your session has been reset. Please use `/model` and `/API` to start again.")

@bot.command()
async def help(ctx):
    help_message = """
    **🤖 AI ChatBot Help Menu**

    Here are the available commands:

    📌 **Model & Token Setup**
    `/model <model_name>` — Set the model you'd like to use  
    `/model status` — Check the currently selected model  
    `/API <your_api_key>` — Set your API token

    💬 **Chatting**
    `/ask <prompt>` — Ask the AI your question or message

    📋 **Info**
    `/help` — Show this help message

        """
    await ctx.send(help_message)



bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
