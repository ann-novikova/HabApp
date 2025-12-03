from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitTestCase(APITestCase):
    """Класс для тестирования CRUD habit"""

    def setUp(self):
        self.user = User.objects.create(email="test@sky.pro")
        self.habit = Habit.objects.create(
            owner=self.user,
            location="Кухня",
            time="19:00",
            action="Выпить кефир",
            is_pleasant=False,
            reward="Сьесть печенье",
            periodicity=1,
            duration=100,
            is_public=True
        )
        self.client.force_authenticate(user=self.user)

    def test_habit_retrieve(self):
        """Тестирование получения деталей привычки"""
        url = reverse("habits:my_habit-detail", args=(self.habit.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("action"), self.habit.action)
