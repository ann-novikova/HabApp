import logging

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from config.celery import app as celery_app

from .models import Habit
from .paginators import HabitsPagination
from .serializers import HabitSerializer
from .services import calculate_reminder_time
from .tasks import send_habit_reminder

logger = logging.getLogger(__name__)


class HabitViewSet(viewsets.ModelViewSet):
    """Контроллер для привычек"""

    serializer_class = HabitSerializer
    pagination_class = HabitsPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        habit = serializer.save(owner=self.request.user)
        reminder_time = calculate_reminder_time(habit.time)
        if reminder_time:
            result = send_habit_reminder.apply_async(args=[habit.pk], eta=reminder_time)
            habit.reminder_task_id = result.id
            habit.save(update_fields=["reminder_task_id"])

    def perform_update(self, serializer):
        original_habit = self.get_object()
        old_task_id = original_habit.reminder_task_id
        habit = serializer.save()
        if old_task_id:
            try:
                celery_app.control.revoke(old_task_id, terminate=True)
            except Exception as e:
                logger.error(
                    f"Ошибка при отмене старого напоминания для привычки ID={habit.pk} (Task ID: {old_task_id}): {e}",
                    exc_info=True,
                )

        reminder_time = calculate_reminder_time(habit.time)

        if reminder_time:
            result = send_habit_reminder.apply_async(args=[habit.pk], eta=reminder_time)
            habit.reminder_task_id = result.id
        else:
            habit.reminder_task_id = None

        habit.save(update_fields=["reminder_task_id"])


class PublicHabitListViewSet(viewsets.ReadOnlyModelViewSet):
    """Контроллер для отображения публичных привычек"""

    serializer_class = HabitSerializer
    pagination_class = HabitsPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)
