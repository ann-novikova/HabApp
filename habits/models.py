from django.db import models

from config import settings

# Create your models here.


class Habit(models.Model):
    """
    Модель для описания привычки в формате:
    Я буду [ДЕЙСТВИЕ] в [ВРЕМЯ] в [МЕСТО]
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Создатель привычки",
        related_name="habits",
    )
    location = models.CharField(max_length=250, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=250, verbose_name="Действие")
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        related_name="related_habits",
    )
    reward = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Вознаграждение",
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Периодичность (в днях)",
    )
    duration = models.PositiveSmallIntegerField(
        verbose_name="Время на выполнение (в секундах)",
        help_text="Не должно превышать 120 секунд.",
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["time"]

    def __str__(self):
        return f"Я буду {self.action} в {self.time} в {self.location}"
