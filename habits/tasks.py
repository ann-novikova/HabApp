import logging
from celery import shared_task
from habits.models import Habit
from .services import send_telegram_message

logger = logging.getLogger(__name__)


@shared_task
def send_habit_reminder(habit_pk):
    """Отправка напоминания через телеграмм"""
    logger.debug(f"DEBUG: Celery worker начал выполнение задачи send_habit_reminder для habit_pk: {habit_pk}")
    try:
        habit = Habit.objects.get(pk=habit_pk)
        user = habit.owner

        logger.info(f"Привычка найдена: '{habit.action}' для пользователя {user.username} (ID: {user.pk})")

        if not user.tg_id:
            logger.warning(f"У пользователя {user.username} (ID: {user.pk}) отсутствует telegram_chat_id.")
            return

        message = (
            f"👋 Напоминание о привычке!\n"
            f"Пора выполнить: {habit.action}\n"
            f"Место: {habit.location}\n"
            f"Длительность: {habit.duration} секунд."
        )
        logger.info(f"Попытка отправки сообщения в Telegram для chat_id: {user.tg_id}")
        send_telegram_message(user.tg_id, message)
        logger.info(f"Сообщение для habit_pk {habit_pk} предположительно отправлено.")

    except Habit.DoesNotExist:
        logger.warning(f"Привычка с ID {habit_pk} не найдена.")
    except Exception as e: # Общий обработчик ошибок для всей задачи
        logger.error(f"Непредвиденная ошибка при выполнении send_habit_reminder для habit_pk {habit_pk}: {e}", exc_info=True)

