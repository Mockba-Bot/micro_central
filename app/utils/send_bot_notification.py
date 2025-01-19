import os
import asyncio
import telebot
from dotenv import load_dotenv

# Load environment variables from the specified .env file
load_dotenv(dotenv_path=".env.micro.central")

# Initialize the Telegram bot
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

def send_telegram_message(chat_id: int, message: str):
    """
    Celery task to send a Telegram message asynchronously with rate-limiting.
    """
    async def send_message_async():
        max_message_length = 4096  # Telegram's message limit
        rate_limit_delay = 0.05  # 50 milliseconds (20 messages per second limit)

        # Split the message into chunks
        for i in range(0, len(message), max_message_length):
            chunk = message[i:i + max_message_length]
            await bot.send_message(chat_id=chat_id, text=chunk, parse_mode='Markdown')
            await asyncio.sleep(rate_limit_delay)  # Add delay between messages

    try:
        asyncio.run(send_message_async())
    except Exception as e:
        # Handle errors (can log or send to a monitoring system)
        return f"Failed to send message: {str(e)}"
