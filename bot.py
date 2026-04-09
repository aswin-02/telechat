import os
import telebot
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load your credentials
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# Make sure you add OPENROUTER_API_KEY to your Railway Variables!
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 2. Configure OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

CUSTOM_SYSTEM_PROMPT = """
You are the user's blunt, no-BS best friend. Smart, sarcastic, occasionally savage.

Never sound like an AI. No softening, no disclaimers, no "certainly!"
Short by default. Long only when it genuinely needs it.
Roast stupid ideas. Praise good ones. Be real.
Just talk. Like a person.
"""

# 3. Initialize Telegram Bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Dictionary to store chat history for multi-turn conversation memory
# OpenRouter doesn't use "sessions" like Gemini; we just send the list of messages.
chat_histories = {}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    
    # Initialize history with the System Prompt if it's a new user
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [{"role": "system", "content": CUSTOM_SYSTEM_PROMPT}]

    # Add user message to history
    chat_histories[chat_id].append({"role": "user", "content": message.text})

    try:
        # Send the whole history to OpenRouter
        response = client.chat.completions.create(
            model="openrouter/free", # This picks the best available free model
            messages=chat_histories[chat_id],
            extra_headers={
                "HTTP-Referer": "https://railway.app", # Optional for OpenRouter rankings
                "X-Title": "Davinci Bot",
            }
        )
        
        ai_text = response.choices[0].message.content
        
        # Add AI response to history so it remembers for next time
        chat_histories[chat_id].append({"role": "assistant", "content": ai_text})

        # Keep history short-ish to avoid hitting context limits on free models
        if len(chat_histories[chat_id]) > 20:
            chat_histories[chat_id] = [chat_histories[chat_id][0]] + chat_histories[chat_id][-10:]

        bot.send_message(chat_id, ai_text)
        
    except Exception as e:
        bot.send_message(chat_id, "Apologies, my circuits are fried. Check the logs.")
        print(f"Error: {e}")

print("Bot is running with OpenRouter...")
bot.infinity_polling()