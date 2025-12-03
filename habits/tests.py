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
            is_public=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_habit_retrieve(self):
        """Тестирование получения деталей привычки"""
        url = reverse("habits:my_habit-detail", args=(self.habit.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("action"), self.habit.action)

    def test_habit_create(self):
        """Тестирование создание привычки"""
        url = reverse("habits:my_habit-list")
        data = {
            "location": "Кухня",
            "time": "08:00",
            "action": "Выпить кофе",
            "is_pleasant": True,
            "periodicity": 1,
            "duration": 100,
            "is_public": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.all().count(), 2)

    def test_habit_update(self):
        """Тестирование обновления деталей привычки"""
        url = reverse("habits:my_habit-detail", args=(self.habit.pk,))
        data = {"action": "Выпить лактобактерии", "is_pleasant": True}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("action"), "Выпить лактобактерии")

    def test_habit_delete(self):
        """Тестирование удаления привычки"""
        url = reverse("habits:my_habit-detail", args=(self.habit.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.all().count(), 0)

    def test_habits_list(self):
        """Тестирование вывода списка привычек"""
        url = reverse("habits:my_habit-list")
        response = self.client.get(url)
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.habit.pk,
                    "owner": self.user.pk,
                    "location": self.habit.location,
                    "time": "19:00:00",
                    "action": self.habit.action,
                    "is_pleasant": self.habit.is_pleasant,
                    "related_habit": None,
                    "periodicity": self.habit.periodicity,
                    "reward": self.habit.reward,
                    "duration": self.habit.duration,
                    "is_public": self.habit.is_public,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), result)
