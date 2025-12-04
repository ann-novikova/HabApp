import logging

from celery import shared_task

from habits.models import Habit

from .services import send_telegram_message

logger = logging.getLogger(__name__)


@shared_task
def send_habit_reminder(habit_pk):
    """Отправка напоминания через телеграмм"""
    logger.debug(
        f"DEBUG: Celery worker начал выполнение задачи send_habit_reminder для habit_pk: {habit_pk}"
    )
    try:
        habit = Habit.objects.get(pk=habit_pk)
        user = habit.owner

        if not user.tg_id:
            return

        message = (
            f"👋 Напоминание о привычке!\n"
            f"Пора выполнить: {habit.action}\n"
            f"Место: {habit.location}\n"
            f"Длительность: {habit.duration} секунд."
        )
        send_telegram_message(user.tg_id, message)
        logger.info(f"Сообщение для habit_pk {habit_pk} предположительно отправлено.")

    except Habit.DoesNotExist:
        logger.warning(f"Привычка с ID {habit_pk} не найдена.")
    except Exception as e:
        logger.error(
            f"Непредвиденная ошибка при выполнении send_habit_reminder для habit_pk {habit_pk}: {e}",
            exc_info=True,
        )
