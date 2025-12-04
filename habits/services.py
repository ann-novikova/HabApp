import requests
import logging
import datetime
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_URL = f"https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage"

def calculate_reminder_time(time):
    """Расчет времени напоминания"""
    now = timezone.now()
    reminder_time_naive = datetime.datetime.combine(now.date(), time)
    reminder_time = timezone.make_aware(reminder_time_naive, timezone.get_current_timezone())

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
        logger.info(
            f"Сообщение успешно отправлено в Telegram для chat_id: {chat_id}. Ответ Telegram API: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ответ Telegram API при ошибке: {e.response.text}")
        return None