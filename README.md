## Disclaimer ⚠️

This bot requires API keys from third-party services. Usage costs and rate limits depend on your chosen providers. Please review each provider's pricing and terms of service.

# Discord AI Chatbot 🤖

A versatile Discord bot that integrates multiple AI providers (Gemini, Groq, OpenAI) to provide chat capabilities, image generation, and reminder functionality.

## Features ✨

- **Multi-AI Provider Support**: Switch between Gemini, Groq, and OpenAI models
- **Conversation History**: Maintains context across messages (last 10 exchanges)
- **Image Generation**: Create images using DALL-E 3
- **Smart Reminders**: Set reminders with natural language time parsing
- **Session Management**: Individual user sessions with usage tracking
- **Secure API Key Handling**: Keys are stored per-user and only accepted via DM

## Supported Models 🧠

### Gemini (Google)
- `gemini-1.5-flash`
- `gemini-1.5-pro` 
- `gemini-pro`

### Groq
- `llama3-8b-8192`
- `llama3-70b-8192`
- `mixtral-8x7b-32768`
- `gemma-7b-it`
- `deepseek-r1-distill-llama-70b`
- `deepseek-r1-distill-llama-8b`

### OpenAI
- `gpt-3.5-turbo`
- `gpt-4`
- `gpt-4o`
- `dall-e-3` (for image generation)

## Installation 🛠️

### Prerequisites
- Python 3.8+
- Discord Bot Token
- API keys for desired AI providers

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/CodrOfTheFuture/LumoGPT.git
   cd LumoGPT
   ```

2. **Install dependencies**
   ```bash
   pip install discord.py python-dotenv google-generativeai openai dateparser
   ```

3. **Create environment file**
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## Getting Discord Bot token 🔑

1. Go to Discord Developer Portal
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the token and add to your `.env` file (NEVER push this file! to prevent this type ".env" in your .gitignore file)

## Commands 📋

### Setup Commands
- `/API <provider> <api_key>` - Set your API key (use in DMs only)
  - Providers: `gemini`, `groq`, `openai`
- `/model <model_name>` - Select which AI model to use
- `/AIstatus` - Check your current model and API key status
- `/reset` - Clear your session and start fresh

### Chat Commands
- `/ask <your_question>` - Chat with the AI
- `/clearhistory` - Clear conversation history
- `/usage` - See how many requests you've made

### Image Generation
- `/image <description>` - Generate an image using DALL-E 3 (requires OpenAI API key)

### Reminder System
- `/remindme <time>` - Set a reminder (e.g., "10 minutes", "2 hours", "tomorrow at 3pm")
  - Can reply to a message to be reminded about that specific message
- `/reminders` - View your active reminders
- `/cancelreminders` - Cancel all your reminders

### Utility
- `/help` - Show help menu

## Bot Permissions Required 📋

When inviting your bot to a server, ensure it has these permissions:
- Send Messages
- Read Message History
- Use Slash Commands
- Embed Links (for image generation)
- Add Reactions (optional, for user feedback)