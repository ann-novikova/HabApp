from rest_framework import serializers

from habits.models import Habit


class HabitValidator:
    def validate_time_success(self, attrs):
        """Проверяет, что время выполнения привычки не превышает 120 секунд."""
        if attrs.get("duration", 0) > 120:
            raise serializers.ValidationError(
                "Время выполнения не должно превышать 120 секунд."
            )

    def validate_related_habit(self, attrs):
        """Проверяет, что в качестве связанной привычки выбрана только приятная привычка."""
        if attrs.get("related_habit"):
            related_habit = Habit.objects.get(pk=attrs.get("related_habit"))
            if not related_habit.is_pleasant:
                raise serializers.ValidationError(
                    "В качестве связанной привычки можно выбрать только приятную привычку."
                )

    def validate_reward_and_related(self, attrs):
        """Проверяет, что не выбраны одновременно и вознаграждение и связанная привычка."""
        if attrs.get("related_habit") and attrs.get("reward"):
            raise serializers.ValidationError(
                "Нельзя одновременно выбирать и связанную привычку и вознаграждение. Выберите что-то одно."
            )

    def validate_pleasant_habit(self, attrs):
        """Проверяет, что приятная привычка не имеет вознаграждения,
        связанной привычки и периодичности выполнения."""
        if attrs.get("is_pleasant"):
            # Приятная привычка не должна иметь вознаграждения
            if attrs.get("reward"):
                raise serializers.ValidationError(
                    "Приятная привычка не может иметь вознаграждения."
                )

            # Приятная привычка не должна быть связана с другой привычкой
            if attrs.get("related_habit"):
                raise serializers.ValidationError(
                    "Приятная привычка не может быть связана с другой привычкой."
                )

    def validate_good_habit_requirements(self, attrs):
        """Проверяет, что полезная привычка имеет либо вознаграждение,
        либо связанную привычку, и имеет периодичность выполнения."""
        if not attrs.get("is_pleasant"):
            # Проверяем, что есть либо вознаграждение, либо связанная привычка
            has_reward_or_related = attrs.get("reward") or attrs.get("related_habit")

            if not has_reward_or_related:
                raise serializers.ValidationError(
                    "Полезная привычка должна иметь либо вознаграждение, либо связанную привычку."
                )

            # Проверяем, что установлена периодичность выполнения
            if not attrs.get("periodicity") or attrs.get("periodicity") > 7:
                raise serializers.ValidationError(
                    "Полезная привычка должна иметь периодичность выполнения."
                )

    def __call__(self, attrs):
        """Основной метод валидации, который вызывает все проверки."""
        self.validate_time_success(attrs)
        self.validate_related_habit(attrs)
        self.validate_reward_and_related(attrs)
        self.validate_pleasant_habit(attrs)
        self.validate_good_habit_requirements(attrs)
