#Modules
import discord
import logging
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai
import openai
from openai import OpenAI
from datetime import datetime, timedelta
import dateparser


load_dotenv()

# variables
discord_token = os.getenv('DISCORD_TOKEN')
usersessions = {}
scheduled_reminders = []

modelLists = {
    "gemini-1.5-flash" : "gemini", 
    "gemini-1.5-pro" : "gemini",
    "gemini-pro": "gemini",
    "llama3-8b-8192": "groq",
    "llama3-70b-8192": "groq",
    "mixtral-8x7b-32768": "groq",
    "gemma-7b-it" : "groq",
    "deepseek-r1-distill-llama-70b": "groq",
    "deepseek-r1-distill-llama-8b": "groq",
    "dall-e-3": "openai",
    "gpt-3.5-turbo": "openai",
    "gpt-4": "openai",
    "gpt-4o": "openai"
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

    if provider not in ["gemini", "groq", "openai"]:
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
    session = usersessions.setdefault(user_id, {})

    model = session.get("model")
    provider = modelLists.get(model)
    api_key = session.get("apis", {}).get(provider)

    if not model:
        await ctx.send("Please set a model first using `/model <model_name>`.")
        return
    if not api_key:
        await ctx.send(f"Missing API key for `{provider}`. Please DM me: `/API {provider} <key>`")
        return

    session["usage_count"] = session.get("usage_count", 0) + 1

    if provider == "gemini":
        try:
            genai.configure(api_key=api_key)
            model_instance = genai.GenerativeModel(model_name=model)
            history = session.setdefault("history", [])
            history.append({"role": "user", "parts": [prompt]})
            response = model_instance.generate_content(history)
            history.append({"role": "model", "parts": [response.text]})
            session["history"] = history[-10:]
            await ctx.send((response.text or "No response.")[:1000])
        except Exception:
            await ctx.send("Error, it looks like the API token is invalid or you do not have enough credits to use this model!")
    elif provider == "groq":
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            history = session.setdefault("history", [])
            history.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model=model,
                messages=history
            )
            reply = response.choices[0].message.content
            history.append({"role": "assistant", "content": reply})
            session["history"] = history[-10:]
            await ctx.send((reply or "No response.")[:1000])
        except Exception as e:
            print(f"Groq API Error: {e}")
            await ctx.send("Error, it looks like the API token is invalid or you do not have enough credits to use this model!")
    elif provider == "openai":
        client = OpenAI(api_key=api_key)
        history = session.setdefault("history", [])
        history.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=model,
            messages=history
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        session["history"] = history[-10:]
        await ctx.send((reply or "No response.")[:1000])
    else:
        await ctx.send("❌ Unsupported model or provider. Please check your setup.")


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
    apis = session.get("apis", {})
    api_status = "✅ Set" if apis else "❌ Not set"

    await ctx.send(
        f"**🔎 Your Session Status:**\n"
        f"• Model: `{model}`\n"
        f"• API Key: `{api_status}`"
    )

@bot.command()
async def image(ctx, *, prompt: str):
    user_id = ctx.author.id
    session = usersessions.get(user_id, {})
    apis = session.get("apis", {})

    openai_key = apis.get("openai")

    if not openai_key:
        if ctx.guild is not None:
            await ctx.send("❌ Please send me your OpenAI API key using `/API openai <key>` in **DMs** to use this command.")
        else:
            await ctx.send("❌ You need to add your OpenAI API key using `/API openai <key>`.")
        return

    await ctx.send(f"🎨 Generating image for: `{prompt}`...")

    try:
        client = OpenAI(api_key=openai_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url

        embed = discord.Embed(
            title="🖼️ DALL·E 3 (OpenAI)",
            description=f"[Click to view full image]({image_url})"
        )
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"OpenAI Image Error: {e}")
        await ctx.send("❌ Failed to generate image using OpenAI. Please check your API key or prompt.")

@bot.command()
async def clearhistory(ctx):
    session = usersessions.get(ctx.author.id, {})
    session["history"] = []
    await ctx.send("🧠 Conversation history cleared.")

@bot.command()
async def usage(ctx):
    session = usersessions.get(ctx.author.id, {})
    usage_count = session.get("usage_count", 0)
    await ctx.send(f"📊 You've made `{usage_count}` requests so far.")


@bot.command()
async def remindme(ctx, *, time_text: str):
    reply_message = ctx.message.reference
    original_message = None

    if reply_message:
        try:
            channel = ctx.channel
            original_message = await channel.fetch_message(reply_message.message_id)
        except:
            await ctx.send("❌ Couldn't fetch the original message you replied to.")
            return

    reminder_time = dateparser.parse(time_text, settings={'PREFER_DATES_FROM': 'future'})
    if not reminder_time:
        await ctx.send("❌ I couldn't understand that time. Try something like `10 minutes` or `2 hours`.")
        return

    delay = (reminder_time - datetime.now()).total_seconds()
    if delay < 0:
        await ctx.send("❌ Time must be in the future.")
        return

    await ctx.send("✅ Reminder set!")

    task = asyncio.create_task(schedule_reminder(ctx.author, original_message, time_text, delay))
    scheduled_reminders.append((ctx.author.id, reminder_time, task))

async def schedule_reminder(user, message, time_text, delay):
    await asyncio.sleep(delay)
    try:
        dm_channel = await user.create_dm()
        if message:
            jump_link = message.jump_url
            await dm_channel.send(f"🔔 Reminder: You asked to be reminded about [this message]({jump_link}).")
        else:
            await dm_channel.send(f"🔔 Reminder: This is your reminder.")
    except Exception as e:
        print(f"DM Reminder Error: {e}")

@bot.command()
async def reminders(ctx):
    now = datetime.now()
    user_reminders = [r for r in scheduled_reminders if r[0] == ctx.author.id]
    if not user_reminders:
        await ctx.send("📭 You have no active reminders.")
        return

    lines = [f"⏰ <t:{int(r[1].timestamp())}:R>" for r in user_reminders if r[1] > now]
    await ctx.send("📋 Your reminders:\n" + "\n".join(lines))

@bot.command()
async def cancelreminders(ctx):
    global scheduled_reminders
    before = len(scheduled_reminders)
    scheduled_reminders = [(uid, t, task) for uid, t, task in scheduled_reminders if uid != ctx.author.id or task.cancel()]
    after = len(scheduled_reminders)
    await ctx.send(f"🗑️ Cancelled {before - after} reminders.")


bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
