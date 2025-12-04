
import datetime
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from habits.models import Habit
from django.utils import timezone # Импортируем timezone для проверки eta

# Предположим, что send_habit_reminder - это задача Celery
# и вы вызываете ее как send_habit_reminder.apply_async(...)
# А celery_app импортируется в habits.views как from your_project.celery import app as celery_app
# Или напрямую из celery: from celery import current_app as celery_app

User = get_user_model()

class HabitTestCase(APITestCase):
    """Класс для тестирования CRUD habit"""

    # В setUp нет патчей
    def setUp(self):
        self.user = User.objects.create(email="test@sky.pro", tg_id="123456789")
        self.user2 = User.objects.create(email="other@sky.pro", tg_id="987654321")
        self.client.force_authenticate(user=self.user)

        self.habit_data = {
            "location": "Кухня",
            "time": datetime.time(19, 0),
            "action": "Выпить кефир",
            "is_pleasant": False,
            "reward": "Съесть печенье",
            "periodicity": 1,
            "duration": 100,
            "is_public": True,
        }
        # Создаем привычку. reminder_task_id будет None, т.к. Celery не запущен
        self.habit = Habit.objects.create(owner=self.user, **self.habit_data)
        # refresh_from_db() здесь не поможет, т.к. в базу ничего не записалось, если нет реального Celery
        # self.assertEqual(self.habit.reminder_task_id, None) # Можете добавить для проверки

        self.list_url = reverse("habits:my_habit-list")
        self.detail_url = reverse("habits:my_habit-detail", args=(self.habit.pk,))


    def test_habit_retrieve(self):
        """Тестирование получения деталей привычки"""
        response = self.client.get(self.detail_url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("action"), self.habit.action)
        self.assertEqual(data.get("owner"), self.user.pk)
        # Теперь self.habit.reminder_task_id будет None, и в данных тоже будет None
        self.assertEqual(data.get("reminder_task_id"), None)


    @patch('habits.views.send_habit_reminder.apply_async')
    def test_habit_create_with_reminder(self, mock_apply_async_method):
        """Тестирование создания привычки с валидным временем напоминания"""
        mock_apply_async_method.return_value = MagicMock(id='mock_task_id_create')
        
        data = {
            "location": "Офис",
            "time": "10:00", # Для API обычно передаем строку
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

        new_habit_id = response.json().get('id')
        self.assertIsNotNone(new_habit_id)
        
        new_habit = Habit.objects.get(id=new_habit_id)
        # new_habit.refresh_from_db() # Не нужно, get() уже дает свежий объект

        self.assertIsNotNone(new_habit.reminder_task_id)
        self.assertEqual(new_habit.reminder_task_id, 'mock_task_id_create')

        mock_apply_async_method.assert_called_once()
        self.assertEqual(mock_apply_async_method.call_args[0][0], [new_habit.pk])
        self.assertIsInstance(mock_apply_async_method.call_args[1]['eta'], timezone.datetime)


    @patch('habits.views.send_habit_reminder.apply_async', return_value=MagicMock(id='mock_task_id_update'))
    @patch('habits.views.celery_app.control.revoke', return_value=True)
    def test_habit_update(self, mock_revoke, mock_apply_async_method):
        """Тестирование обновления деталей привычки"""
        url = reverse("habits:my_habit-detail", args=(self.habit.pk,))
        data = {"action": "Выпить лактобактерии", "is_pleasant": True, "time": "09:00"}
        
        # Теперь old_task_id будет None, т.к. self.habit изначально не имеет task_id
        old_task_id = self.habit.reminder_task_id
        self.assertIsNone(old_task_id) # Подтверждаем, что он None

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.habit.refresh_from_db() # Обновляем привычку из БД после PATCH

        self.assertEqual(self.habit.action, "Выпить лактобактерии")
        
        # Теперь reminder_task_id должен быть установлен новым вызовом Celery
        self.assertIsNotNone(self.habit.reminder_task_id)
        self.assertEqual(self.habit.reminder_task_id, 'mock_task_id_update')

        # Если ваша логика revoke() сначала проверяет, есть ли task_id,
        # то mock_revoke не должен был вызываться, т.к. old_task_id был None.
        # Если ваша логика вызывает revoke(None) (что может быть ошибкой в реальном коде),
        # то mock_revoke.assert_called_once_with(None)
        # Я предполагаю, что код будет достаточно надежным и не вызовет revoke для None.
        mock_revoke.assert_not_called() 

        mock_apply_async_method.assert_called_once_with([self.habit.pk], eta=mock_apply_async_method.call_args[1]['eta'])
        self.assertIsInstance(mock_apply_async_method.call_args[1]['eta'], timezone.datetime)


    @patch('habits.views.celery_app.control.revoke', return_value=True)
    def test_habit_delete(self, mock_revoke):
        """Тестирование удаления привычки"""
        url = reverse("habits:my_habit-detail", args=(self.habit.pk,))
        
        # task_id_to_revoke будет None, т.к. self.habit не имеет task_id
        task_id_to_revoke = self.habit.reminder_task_id
        self.assertIsNone(task_id_to_revoke) # Подтверждаем, что он None

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.all().count(), 0)

        # Аналогично revoke при обновлении: если нет task_id, revoke не должен вызываться.
        mock_revoke.assert_not_called()


    def test_habit_list(self):
        """Тестирование получения списка привычек"""

        # Для этой привычки также не будет reminder_task_id
        habit_other_user = Habit.objects.create(
            owner=self.user2,
            location="Гостиная",
            time=datetime.time(10, 0),
            action="Почитать книгу",
            is_pleasant=True,
            periodicity=1,
            duration=60,
            is_public=False
        )
        # habit_other_user.refresh_from_db() # Не нужно, т.к. нет task_id для получения

        response = self.client.get(self.list_url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["action"], self.habit.action)
        self.assertEqual(data["results"][0]["owner"], self.user.pk)
        # self.habit.reminder_task_id будет None, и в данных тоже
        self.assertEqual(data["results"][0]["reminder_task_id"], None)

