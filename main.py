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
async def API(ctx, provider: str, *, key: str):
    user_id = ctx.author.id

    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("❌ Please DM me your API keys, don't share them in public.")
        return

    if provider not in ["gemini", "groq"]:
        await ctx.send("❌ Invalid provider. Supported: gemini and groq (for now)")
        return

    session = usersessions.setdefault(user_id, {})
    session.setdefault("apis", {})[provider] = key
    await ctx.send(f"✅ Your `{provider}` API key has been saved.")

@bot.command()
async def model(ctx, *, message):
    user_id = ctx.author.id
    session = usersessions.setdefault(user_id, {})

    if message not in modelLists:
        model_names = ', '.join(modelLists.keys())
        await ctx.send(f"Invalid model type. Valid models: {model_names}")
        return

    session["model"] = message
    await ctx.send(f"Model has been set to {message}!")


@bot.command()
async def ask(ctx, *, prompt: str):
    user_id = ctx.author.id
    session = usersessions.get(user_id, {})

    model = session.get("model")
    provider = modelLists.get(model)
    api_key = session.get("apis", {}).get(provider)

    if not model:
        await ctx.send("Please set a model first using `/model <model_name>`.")
        return
    if not api_key:
        await ctx.send(f"Missing API key for `{provider}`. Please DM me: `/API {provider} <key>`")
        return

    if provider == "gemini":
        await askGemini(ctx, prompt, model, api_key)
    elif provider == "groq":
        await askGroq(ctx, prompt, model, api_key)
    else:
        await ctx.send("Unsupported provider.")

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

@bot.command()
async def AIstatus(ctx):
    user_id = ctx.author.id
    session = usersessions.get(user_id, {})

    model = session.get("model", "❌ Not set")
    api = "✅ Set" if "api" in session else "❌ Not set"

    await ctx.send(
        f"**🔎 Your Session Status:**\n"
        f"• Model: `{model}`\n"
        f"• API Key: `{api}`"
    )


bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
