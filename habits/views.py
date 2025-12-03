from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
import datetime

from .services import calculate_reminder_time
from .tasks import send_habit_reminder

from .models import Habit
from .paginators import HabitsPagination
from .serializers import HabitSerializer


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
        send_habit_reminder.apply_async(
            args=[habit.pk],
            eta=reminder_time
        )

    def perform_update(self, serializer):
        habit = serializer.save()
        reminder_time = calculate_reminder_time(habit.time)
        send_habit_reminder.apply_async(
            args=[habit.pk],
            eta=reminder_time
        )



class PublicHabitListViewSet(viewsets.ReadOnlyModelViewSet):
    """Контроллер для отображения публичных привычек"""

    serializer_class = HabitSerializer
    pagination_class = HabitsPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)
