import os
import telebot
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load your credentials
# You can also just hardcode strings here if you're not using .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY =  os.getenv("API_KEY")

# 2. Configure Gemini with a CUSTOM PROMPT
genai.configure(api_key=GEMINI_API_KEY)

# This is where you define your bot's personality or rules
CUSTOM_SYSTEM_PROMPT = """
You are a highly intelligent and straightforward friend with a sharp, sarcastic sense of humor.

- Give clear, accurate, and practical answers
- Keep responses medium-length (not too short, not long paragraphs)
- Be witty and lightly roast the user, but keep it playful
- Call out bad ideas directly, but don’t be harsh or offensive
- Avoid unnecessary fluff or over-explaining
- Focus on solving the problem efficiently

davinci is the one who created you.
"""
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=CUSTOM_SYSTEM_PROMPT
)

# 3. Initialize Telegram Bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Dictionary to store chat sessions for multi-turn conversation memory
chat_sessions = {}

@bot.message_handler(func=lambda message: True)
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    
    # Start a new session if it doesn't exist
    if chat_id not in chat_sessions:
        chat_sessions[chat_id] = model.start_chat(history=[])

    try:
        # Send user message to Gemini
        response = chat_sessions[chat_id].send_message(message.text)
        
        # USE THIS instead of bot.reply_to:
        bot.send_message(chat_id, response.text)
        
    except Exception as e:
        bot.send_message(chat_id, "Apologies, I've encountered an error.")
        print(f"Error: {e}")

print("Bot is running...")
bot.infinity_polling()