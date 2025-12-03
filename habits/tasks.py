from celery import shared_task
from habits.models import Habit
from users.models import User
from .services import send_telegram_message
import datetime


@shared_task
def send_habit_reminder(habit_pk):
    """Задача для отправки напоминания о конкретной привычке."""
    try:
        habit = Habit.objects.get(pk=habit_pk)
        user = habit.owner

        if not user.telegram_chat_id:
            print(f"Пользователь {user.email} не имеет привязанного Chat ID.")
            return

        message = (
            f"👋 Напоминание о привычке!\n"
            f"Пора выполнить: {habit.action}\n"
            f"Место: {habit.location}\n"
            f"Длительность: {habit.duration} секунд."
        )

        send_telegram_message(user.telegram_chat_id, message)

    except Habit.DoesNotExist:
        print(f"Привычка с ID {habit_pk} не найдена.")