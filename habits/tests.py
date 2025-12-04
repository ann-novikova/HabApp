from datetime import time
from unittest.mock import MagicMock, patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitTestCase(APITestCase):
    """Класс для тестирования CRUD habit"""

    def setUp(self):
        self.user = User.objects.create(
            email="test@sky.pro", tg_id="123456789"
        )  # Добавим tg_id для тестов
        self.user2 = User.objects.create(
            email="other@sky.pro", tg_id="987654321"
        )  # Для проверки доступа
        self.client.force_authenticate(user=self.user)

        self.habit_data = {
            "location": "Кухня",
            "time": time(19, 0),
            "action": "Выпить кефир",
            "is_pleasant": False,
            "reward": "Съесть печенье",
            "periodicity": 1,
            "duration": 100,
            "is_public": True,
        }
        self.habit = Habit.objects.create(owner=self.user, **self.habit_data)

        self.list_url = reverse("habits:my_habit-list")
        self.detail_url = reverse("habits:my_habit-detail", args=(self.habit.pk,))

    def test_habit_retrieve(self):
        """Тестирование получения деталей привычки"""
        response = self.client.get(self.detail_url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("action"), self.habit.action)
        self.assertEqual(data.get("owner"), self.user.pk)

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

    def test_habit_list(self):
        """Тестирование получения списка привычек"""

        Habit.objects.create(
            owner=self.user2,
            location="Гостиная",
            time=time(10, 0),
            action="Почитать книгу",
            is_pleasant=True,
            periodicity=1,
            duration=60,
            is_public=False,
        )
        response = self.client.get(self.list_url)
        data = response.json()  # Фактический результат

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            data["count"], 1
        )  # Должна быть только 1 привычка текущего пользователя
        self.assertEqual(data["results"][0]["action"], self.habit.action)
        self.assertEqual(data["results"][0]["owner"], self.user.pk)
        self.assertEqual(
            data["results"][0]["reminder_task_id"], self.habit.reminder_task_id
        )

    @patch("habits.views.send_habit_reminder.apply_async")
    def test_habit_create_with_reminder(self, mock_apply_async_method):
        """Тестирование создания привычки с валидным временем напоминания"""
        mock_apply_async_method.return_value = MagicMock(id="mock_task_id_create")

        data = {
            "location": "Офис",
            "time": "10:00",  # Для API обычно передаем строку
            "action": "Проверить почту",
            "is_pleasant": False,
            "reward": "Выпить кофе",
            "periodicity": 1,
            "duration": 60,
            "is_public": False,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.all().count(), 2)

        new_habit_id = response.json().get("id")
        self.assertIsNotNone(new_habit_id)

        new_habit = Habit.objects.get(id=new_habit_id)
        # new_habit.refresh_from_db() # Не нужно, get() уже дает свежий объект

        self.assertIsNotNone(new_habit.reminder_task_id)
        self.assertEqual(new_habit.reminder_task_id, "mock_task_id_create")

        mock_apply_async_method.assert_called_once()
        self.assertEqual(mock_apply_async_method.call_args[1]["args"], [new_habit.pk])
        self.assertIsInstance(
            mock_apply_async_method.call_args[1]["eta"], timezone.datetime
        )

    @patch(
        "habits.views.send_habit_reminder.apply_async",
        return_value=MagicMock(id="mock_task_id_update"),
    )
    @patch("habits.views.celery_app.control.revoke", return_value=True)
    def test_habit_update_with_reminder(self, mock_revoke, mock_apply_async_method):
        """Тестирование обновления деталей привычки"""
        url = reverse("habits:my_habit-detail", args=(self.habit.pk,))
        data = {"action": "Выпить лактобактерии", "is_pleasant": True, "time": "09:00"}

        # Теперь old_task_id будет None, т.к. self.habit изначально не имеет task_id
        old_task_id = self.habit.reminder_task_id
        self.assertIsNone(old_task_id)  # Подтверждаем, что он None

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.habit.refresh_from_db()  # Обновляем привычку из БД после PATCH

        self.assertEqual(self.habit.action, "Выпить лактобактерии")

        self.assertIsNotNone(self.habit.reminder_task_id)
        self.assertEqual(self.habit.reminder_task_id, "mock_task_id_update")

        mock_revoke.assert_not_called()

        mock_apply_async_method.assert_called_once_with(
            args=[self.habit.pk], eta=mock_apply_async_method.call_args[1]["eta"]
        )
        self.assertIsInstance(
            mock_apply_async_method.call_args[1]["eta"], timezone.datetime
        )

    def test_unauthenticated_access(self):
        """Тестирование неавторизованного доступа"""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(self.list_url, self.habit_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.detail_url, {"action": "test"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
