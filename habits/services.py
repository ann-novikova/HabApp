import requests
import datetime
from django.conf import settings

TELEGRAM_URL = f"https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage"

def calculate_reminder_time(time):
    now = datetime.datetime.now()
    reminder_time = datetime.datetime.combine(now.date(), time)

    # Если время уже прошло, планируем на завтра
    if reminder_time <= now:
        reminder_time += datetime.timedelta(days=1)

    return reminder_time

def send_telegram_message(chat_id, message):
    """Отправляет сообщение через Telegram Bot API."""

    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(TELEGRAM_URL, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки Telegram: {e}")
        return None