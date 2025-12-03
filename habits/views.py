from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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
        serializer.save(owner=self.request.user)


class PublicHabitListViewSet(viewsets.ReadOnlyModelViewSet):
    """Контроллер для отображения публичных привычек"""

    serializer_class = HabitSerializer
    pagination_class = HabitsPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)
