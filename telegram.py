import os
import requests

# Replace 'YOUR_BOT_TOKEN' with the actual token of your bot
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Define the base URL for the Telegram Bot API
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/'


def send_message(chat_id, topic_id, text):
    url = BASE_URL + 'sendMessage'
    params = {'chat_id': chat_id, 'message_thread_id': topic_id, 'text': text}
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()


def get_me():
    url = BASE_URL + 'getMe'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
